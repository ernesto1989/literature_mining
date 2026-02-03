# Literature mining proyect
#
# Minería de literatura científica para la extracción de información relevante.
#
# El proyecto consta de los siguientes módulos:
# 1. El query builder (src/query_builder.py) que construye queries robustos para Scopus.
# 2. El main (src/main.py) que ejecuta las búsquedas en Scopus y guarda los resultados en un archivo Excel.
#
# Por búsqueda, se construye actualmente un archivo excel con la fecha de consulta, en donde se especifica:
# 1. Por un lado se registra el query utilizado, las keywords, el rango de años y el total de resultados obtenidos.
# 2. Por otro lado, se guarda una hoja con los papers obtenidos, incluyendo título, autores, número de citas y enlace a Scopus.
#
# Eventualmente, se pretende utilizar una BD relacional para determinar referencias cruzadas entre papers, autores, instituciones y países.
# De esta forma, se podrá realizar análisis más profundos sobre la literatura científica en un área específica.
# 
#
# Ernesto Cantú
# Monterrey, México
# 26 Enero 2026


from datetime import datetime
import pandas as pd
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import pybliometrics.scopus as sc
from query_builder import build_scopus_query as query_builder
from pybliometrics.exception import Scopus400Error

from dotenv import load_dotenv
import os


def main():

    keywords = ["xai", "business"]
    year_from = 2020
    year_to = 2025

    query = query_builder(
        keywords=keywords,
        year_from=year_from,
        year_to=year_to,
        doctype="ar"
    )
    print(f"Query construido:\n{query}\n")
    
    #Configs scopus
    sc.init()

    try:
        #s = ScopusSearch(query, count=25)
        s = ScopusSearch(query,subscriber=False,count=25) 
    except Scopus400Error as e:
        print("Cuota agotada. Deteniendo ejecución.")
        exit(1)
    
    # print(s.get_results_size())
    # print(f"\nResultados: {s.get_results_size()}")
    # for r in s.results:
    #     print(f"- {r.title} | citas: {r.citedby_count}")

    total_results = s.get_results_size()
    # =========================
    # QUERY LOG (1 fila)
    # =========================
    query_log = pd.DataFrame([{
        "fecha_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "keywords": ", ".join(keywords),
        "start_year": year_from,
        "end_year": year_to,
        "total_resultados": total_results,
        "query": query
    }])

    # =========================
    # PAPERS
    # =========================
    papers_data = []

    for r in s.results:
        papers_data.append({
            "eid": r.eid,
            "title": r.title,
            "authors": r.author_names,
            "cited_by": r.citedby_count,
            "scopus_url": f"https://www.scopus.com/record/display.uri?eid={r.eid}&origin=resultslist"
        })

    papers_df = pd.DataFrame(papers_data)

    # =========================
    # WRITE EXCEL
    # =========================
    with pd.ExcelWriter(f'C:/Conciencia/LIT_MINING_OUTPUT/scopus_output_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx', engine="openpyxl") as writer:
        query_log.to_excel(writer, sheet_name="query_log", index=False)
        papers_df.to_excel(writer, sheet_name="papers", index=False)

    print(f"Archivo generado: C:/Conciencia/LIT_MINING_OUTPUT/scopus_output_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx")
    print(f"Total papers: {len(papers_df)}")

if __name__ == "__main__":
    main()

    
    
    
    
    