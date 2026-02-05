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

import pybliometrics.scopus as sc
from query_builder import build_scopus_query as query_builder

from excel_output import save_to_excel
from scopus_search import scopus_search
import os
from dotenv import load_dotenv

def read_parameters():
    """
        Función que lee los parámetros de entrada desde un archivo .env.
        Por implementar.
    """
    load_dotenv()            
    keywords = os.getenv("KEYWORDS", "methodology,auditing,ai").split(",")
    keywords = [k.strip() for k in keywords]
    year_from = int(os.getenv("YEAR_FROM", "2020"))
    year_to = int(os.getenv("YEAR_TO", "2025"))
    output_file_path = os.getenv("OUTPUT_FILE_PATH", "C:/Conciencia/LIT_MINING_OUTPUT/")
    output_file_name = os.getenv("OUTPUT_FILE_NAME", "scopus_mining.xlsx")
    write_to_rdbms = os.getenv("WRITE_TO_RDBMS", "False").lower() == "true"
    return keywords, year_from, year_to, output_file_path, output_file_name, write_to_rdbms

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

    # --- Configuración ---
    keywords, year_from, year_to, output_file_path, output_file_name, write_to_rdbms = read_parameters()
   
    query = query_builder(keywords=keywords,year_from=year_from,year_to=year_to,doctype="ar")
    print(f"Query construido:\n{query}\n")
    
    query_log_row, papers_df, sheet_name_papers = scopus_search(
        query,
        keywords,
        year_from,
        year_to
    )

    if not write_to_rdbms:
        save_to_excel(output_file_path, output_file_name, sheet_name_papers, query_log_row, papers_df)
    else:
        pass



if __name__ == "__main__":
    main()