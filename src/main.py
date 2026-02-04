from datetime import datetime
import pandas as pd
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import pybliometrics.scopus as sc
from query_builder import build_scopus_query as query_builder
from pybliometrics.exception import Scopus400Error
import os
import uuid
import time

def main():
    # --- Configuración ---
    keywords = ["xai", "business"]
    year_from = 2020
    year_to = 2025
    output_file_path = "C:/Conciencia/LIT_MINING_OUTPUT/"
    output_file_name = "scopus_mining.xlsx"
    full_path = os.path.join(output_file_path, output_file_name)

    # Asegurar que la carpeta existe
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    query = query_builder(
        keywords=keywords,
        year_from=year_from,
        year_to=year_to,
        doctype="ar"
    )
    print(f"Query construido:\n{query}\n")
    
    sc.init()

    try:
        # Nota: count=25 es el máximo para no suscriptores por petición
        s = ScopusSearch(query, subscriber=True, count=25) 
    except Scopus400Error:
        print("Cuota agotada o error en la petición. Deteniendo ejecución.")
        return

    # --- Generación de Identificadores ---
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
                #print(f"[{i+1}/{len(s.results)}] Recuperando autores detallados para EID: {r.eid}...")
                ab = AbstractRetrieval(r.eid, view="META")
                if ab.authors:
                    # 1. Concatenamos los IDs de los autores (separados por ;)
                    author_ids = "; ".join([str(a.auid) for a in ab.authors])
                    
                    # 2. Concatenamos los Nombres de los autores (separados por ;)
                    author_names = "; ".join([f"{a.surname}, {a.given_name}" for a in ab.authors])
                else:
                    author_ids = "N/D"
                    author_names = "N/D"
                
                # Un pequeño delay para no saturar la API si son muchos registros
                time.sleep(0.2) 
            except Exception as e:
                authors = f"Error al recuperar: {str(e)}"

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

    # --- Escritura en Excel ---
    file_exists = os.path.exists(full_path)

    if not file_exists:
        with pd.ExcelWriter(full_path, engine="openpyxl", mode="w") as writer:
            query_log_row.to_excel(writer, sheet_name="query_log", index=False)
            papers_df.to_excel(writer, sheet_name=sheet_name_papers, index=False)
    else:
        # Corregido: Cargamos el log existente usando la ruta correcta
        existing_log = pd.read_excel(full_path, sheet_name="query_log")
        query_log_final = pd.concat([existing_log, query_log_row], ignore_index=True)

        with pd.ExcelWriter(
            full_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:
            query_log_final.to_excel(writer, sheet_name="query_log", index=False)
            papers_df.to_excel(writer, sheet_name=sheet_name_papers, index=False)

    print(f"\nProceso finalizado. Archivo guardado en: {full_path}")

if __name__ == "__main__":
    main()