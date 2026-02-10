# Literature mining proyect
#
# Minería de literatura científica para la extracción de información relevante.
#
# El proyecto consta de los siguientes módulos:
# 1. Query builder (src/query_builder.py) que construye los queries para Scopus.
# 2. Scopus search (src/scopus_search.py) que realiza la consulta al API de Scopus a través de pybliometrics y procesa los resultados.
# 3. Excel output (src/excel_output.py) que realiza la escritura a un archivo excel.
# 4. Rdbms output (src/rdbms_output.py) que realizará la escritura a una base de datos relacional (por implementar).
# 5. Main (src/main.py) que ejecuta las búsquedas en Scopus y guarda los resultados en un archivo Excel.
#
# En la salida de excel se construye actualmente un archivo excel con la fecha de consulta, en donde se especifica:
# 1. Por un lado se registra el query utilizado, las keywords, el rango de años y el total de resultados obtenidos en la pestaña de query_log.
# 2. Por otro lado, se guarda una hoja con los papers obtenidos, incluyendo título, autores, número de citas y enlace a Scopus.
#
# Eventualmente, se pretende utilizar una BD relacional para determinar referencias cruzadas entre papers, autores, instituciones y países.
# De esta forma, se podrá realizar análisis más profundos sobre la literatura científica en un área específica.
# 
#
# Ernesto Cantú
# Monterrey, México
# 26 Enero 2026

import pybliometrics.scopus as sc
from query_builder import build_scopus_query as query_builder

from excel_output import save_to_excel
from rdbms_output import save_to_db
from scopus_search import scopus_search
import os
from pathlib import Path
from dotenv import load_dotenv
import argparse

def read_env():
    """
        Función que lee los parámetros de entrada desde un archivo .env.
        Por implementar.
    """
    load_dotenv()            
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "tu_usuario")
    password = os.getenv("MYSQL_PASSWORD", "tu_password")
    db = os.getenv("MYSQL_DB", "scopus_db")
    return  host, port, user, password, db

def main():
    """
        1. Leer parámetros. Keywords, años, path de salida y tipo de documento (falta el último).
        2. Construir el query a partir de los parámetros de entrada.
        3. Ejecutar la búsqueda en Scopus.
        4. Procesar los resultados y construir los dataframes.
        5. Escribir los resultados en la salida correspondiente:
            a) Excel - Implementado
            b) Base de datos Relacional- Por implementar
    """

    # --- Configuración (desde argumentos CLI) ---
    parser = argparse.ArgumentParser(description="Scopus literature mining")
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Space-separated keywords (e.g. --keywords machine learning ai)",
        default=["methodology", "auditing", "ai", "business"]
    )
    parser.add_argument("--year-from", type=int, dest="year_from", default=2019, help="Start year")
    parser.add_argument("--year-to", type=int, dest="year_to", default=2025, help="End year")
    parser.add_argument("--write-to-db", action="store_true", dest="write_to_db", help="Write results to DB instead of Excel")
    args = parser.parse_args()

    keywords = args.keywords
    year_from = args.year_from
    year_to = args.year_to
    write_to_db = args.write_to_db
    
    query = query_builder(keywords=keywords,year_from=year_from,year_to=year_to,doctype="ar")
    print(f"Query construido:\n{query}\n")
    

    if not write_to_db:
        # Archivo de Salida
        output_file_path = "C:/Conciencia/LIT_MINING_OUTPUT/"
        output_file_name = "scopus_mining.xlsx"

        query_log_row, papers_df, sheet_name_papers = scopus_search(
            query,
            keywords,
            year_from,
            year_to,
            False
        )
        save_to_excel(output_file_path, output_file_name, sheet_name_papers, query_log_row, papers_df)
    else:
        host, port, user, password, db = read_env()
        query_log, papers_to_db, authors_to_db_list, relations_to_db, references_to_db = scopus_search(
            query,
            keywords,
            year_from,
            year_to,
            True
        )
        save_to_db(host, port, user, password, db, keywords, query_log, papers_to_db, authors_to_db_list, relations_to_db,references_to_db)


if __name__ == "__main__":
    main()