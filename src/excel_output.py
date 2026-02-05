#
# Script que realiza la escritura a un archivo excel.
# 
# Ernesto Cantú
# 04 de febrero de 2026
#

import pandas as pd
import os
from datetime import datetime


def save_to_excel(output_file_path, output_file_name, sheet_name_papers, query_log_df, papers_df):
    """
        Función que realiza la escritura de los dataframes a un archivo Excel.
        Recibe:

        1. output_file_path: Ruta donde se guardará el archivo.
        2. output_file_name: Nombre del archivo Excel.
        3. sheet_name_papers: Nombre de la hoja donde se guardarán los papers.
        4. query_log_df: DataFrame con el log de la consulta.
        5. papers_df: DataFrame con los papers obtenidos.

        Valida la existencia de la carpeta contenedora (path) y del archivo.
        Si no existe el archivo, lo crea y escribe ambos dataframes.
        Si ya existe, agrega el log a la hoja "query_log" y crea la pestaña con los paper de la consulta actual.
    """
    # Asegurar que la carpeta existe
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    full_path = os.path.join(output_file_path, output_file_name)
    
    # --- Escritura en Excel ---
    file_exists = os.path.exists(full_path)

    if not file_exists:
        with pd.ExcelWriter(full_path, engine="openpyxl", mode="w") as writer:
            query_log_df.to_excel(writer, sheet_name="query_log", index=False)
            papers_df.to_excel(writer, sheet_name=sheet_name_papers, index=False)
    else:
        # Corregido: Cargamos el log existente usando la ruta correcta
        existing_log = pd.read_excel(full_path, sheet_name="query_log")
        query_log_final = pd.concat([existing_log, query_log_df], ignore_index=True)

        with pd.ExcelWriter(
            full_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:
            query_log_final.to_excel(writer, sheet_name="query_log", index=False)
            papers_df.to_excel(writer, sheet_name=sheet_name_papers, index=False)
    print(f"\nProceso finalizado. Archivo guardado en: {full_path}")
    return