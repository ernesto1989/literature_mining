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

def scopus_search(query, keywords, year_from, year_to):
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