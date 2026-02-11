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

def prepare_for_db(s,keywords, year_from, year_to, query,log_id_short,fecha_hoy):
    """
        Prepara las estructuras para su escritura en la base de datos relacional.
        Por implementar.
    """   
    # Estructuras para la DB
    papers_to_db = []
    authors_to_db = set() # Usamos set para evitar duplicados en memoria
    relations_to_db = []
    references_to_db = []
    paper_query_relations = [] # Para relacionar eid con la consulta (log_id)

    print(f"Procesando {len(s.results)} resultados...")

    for r in s.results:
        try:
            ab = AbstractRetrieval(r.eid, view="FULL")
            
            # Datos del Paper
            papers_to_db.append((
                r.eid, 
                r.title, 
                ab.subtype,
                r.citedby_count, 
                f"https://www.scopus.com/record/display.uri?eid={r.eid}"
            ))

            paper_query_relations.append((log_id_short, r.eid))

            if ab.authors:
                for auth in ab.authors:
                    a_id = str(auth.auid)
                    a_name = f"{auth.surname}, {auth.given_name}"
                    
                    authors_to_db.add((a_id, a_name))
                    relations_to_db.append((r.eid, a_id))

            if ab.references:
                for ref in ab.references:
                    generated_url = None

                    if ref.id:
                        generated_url = f"https://www.scopus.com/record/display.uri?eid={ref.id}&origin=resultslist"
                    
                    # Prioridad 2: Si no hay EID pero hay DOI
                    elif hasattr(ref, 'doi') and ref.doi:
                        generated_url = f"https://doi.org/{ref.doi}"

                    references_to_db.append((
                        r.eid,           # El paper origen
                        ref.id,          # ID de la referencia en Scopus (si tiene)
                        ref.title,       # Título del paper citado
                        ref.authors,     # Autores citados
                        #ref.year,         # Año de la cita
                        generated_url
                    ))
            
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
    return query_log, papers_to_db, list(authors_to_db), relations_to_db,references_to_db,paper_query_relations
    


def scopus_search(query, keywords, year_from, year_to,save_to_db=False):
    """
        Realiza la búsqueda en Scopus usando el query proporcionado.
        Retorna un DataFrame con los resultados procesados.
    """
    sc.init()
    try:
        # Nota: count=25 es el máximo para no suscriptores por petición
        s = ScopusSearch(query, subscriber=False, count=25) 
    except Scopus400Error:
        print("Cuota agotada o error en la petición. Deteniendo ejecución.")
        return
    
    # Usamos solo 8 caracteres del UUID para no exceder los 31 caracteres en la pestaña de Excel
    log_id_short = str(uuid.uuid4())[:8]
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query_log, papers_to_db, authors_to_db_list, relations_to_db,references_to_db,paper_query_relations = prepare_for_db(s, keywords, year_from, year_to, query, log_id_short, fecha_hoy)
    return query_log, papers_to_db, authors_to_db_list, relations_to_db, references_to_db,paper_query_relations

   