#
# Archivo que realiza la consulta al api de Scopus a través de pybliometrics.
# Genera los DF's correspondientes y retorna el resultado de la búsqueda ya procesado
#
# Ernesto Cantú
# 4 de febrero de 2026

import pandas as pd
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import pybliometrics.scopus as sc
from pybliometrics.exception import Scopus400Error

from datetime import datetime
import uuid
import time

def prepare_for_excel(s,keywords, year_from, year_to, query,log_id_short,fecha_hoy):
    """
        Prepara los dataframes para su escritura en Excel.
        Por implementar.
    """
    

    # --- Query Log ---
    total_results = s.get_results_size()
    query_log_row = pd.DataFrame([{
        "log_id": log_id_short,
        "fecha_consulta": fecha_hoy,
        "keywords": ", ".join(keywords),
        "start_year": year_from,
        "end_year": year_to,
        "total_resultados": total_results,
        "query": query
    }])

    # --- Procesamiento de Papers ---
    papers_data = []
    print(f"Procesando {len(s.results)} resultados...")

    for i, r in enumerate(s.results):
        # Intentar obtener autores del resultado de búsqueda
        author_ids = r.author_ids
        author_names = r.author_names
        
        # Si vienen vacíos (común en modo no-suscriptor), usamos AbstractRetrieval
        if not author_names:
            try:
                ab = AbstractRetrieval(r.eid, view="META")
                if ab.authors:
                    author_ids = "; ".join([str(a.auid) for a in ab.authors])
                    author_names = "; ".join([f"{a.surname}, {a.given_name}" for a in ab.authors])
                else:
                    author_ids = "N/D"
                    author_names = "N/D"
                
                # Un pequeño delay para no saturar la API si son muchos registros
                time.sleep(0.2) 
            except Exception as e:
                author_names = f"Error al recuperar: {str(e)}"

        papers_data.append({
            "eid": r.eid,
            "title": r.title,
            "author_ids": author_ids,   # Columna de IDs (Antes)
            "authors": author_names,
            "cited_by": r.citedby_count,
            "scopus_url": f"https://www.scopus.com/record/display.uri?eid={r.eid}&origin=resultslist"
        })

    papers_df = pd.DataFrame(papers_data)
    sheet_name_papers = f"p_{log_id_short}" # Nombre corto (máx 31 caracteres)

    return query_log_row, papers_df, sheet_name_papers



def prepare_for_db(s,keywords, year_from, year_to, query,log_id_short,fecha_hoy):
    """
        Prepara las estructuras para su escritura en la base de datos relacional.
        Por implementar.
    """   
    # Estructuras para la DB
    papers_to_db = []
    authors_to_db = set() # Usamos set para evitar duplicados en memoria
    relations_to_db = []

    print(f"Procesando {len(s.results)} resultados...")

    for r in s.results:
        try:
            ab = AbstractRetrieval(r.eid, view="META")
             # Intentar obtener autores del resultado de búsqueda
            author_ids = r.author_ids
            author_names = r.author_names
            # Datos del Paper
            papers_to_db.append((
                r.eid, 
                r.title, 
                r.citedby_count, 
                f"https://www.scopus.com/record/display.uri?eid={r.eid}"
            ))

            # Datos de Autores y Relaciones
            # Usar author_ids y author_names que vienen del resultado de búsqueda
            if author_ids and author_names:
                ids_list = [id.strip() for id in str(author_ids).split(";")]
                names_list = [name.strip() for name in str(author_names).split(";")]
                for auth_id, auth_name in zip(ids_list, names_list):
                    # Guardamos autor en el set (author_id, name)
                    authors_to_db.add((auth_id, auth_name))
                    # Guardamos la relación (eid, author_id)
                    relations_to_db.append((r.eid, auth_id))
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Error en {r.eid}: {e}")

    # Preparar el log
    query_log = (
        log_id_short, 
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
        ", ".join(keywords), 
        year_from, 
        year_to, 
        len(papers_to_db), 
        query
    )

    # Mandar todo a la base de datos
    return query_log, papers_to_db, list(authors_to_db), relations_to_db
    


def scopus_search(query, keywords, year_from, year_to,save_to_db=False):
    """
        Realiza la búsqueda en Scopus usando el query proporcionado.
        Retorna un DataFrame con los resultados procesados.
    """
    sc.init()
    try:
        # Nota: count=25 es el máximo para no suscriptores por petición
        s = ScopusSearch(query, subscriber=True, count=25) 
    except Scopus400Error:
        print("Cuota agotada o error en la petición. Deteniendo ejecución.")
        return
    
    # Usamos solo 8 caracteres del UUID para no exceder los 31 caracteres en la pestaña de Excel
    log_id_short = str(uuid.uuid4())[:8]
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not save_to_db:
        query_log_row, papers_df, sheet_name_papers = prepare_for_excel(s, keywords, year_from, year_to, query, log_id_short, fecha_hoy)
        return query_log_row, papers_df, sheet_name_papers
    else:
        query_log, papers_to_db, authors_to_db_list, relations_to_db = prepare_for_db(s, keywords, year_from, year_to, query, log_id_short, fecha_hoy)
        return query_log, papers_to_db, authors_to_db_list, relations_to_db

   