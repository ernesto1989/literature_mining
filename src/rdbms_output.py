#
# Salida a SQLite para realizar mayor análisis relacionales en el futuro.
#
# Ernesto Cantú
# 4 de febrero de 2026
#

import mysql
from mysql.connector import Error

def save_to_db(host,port,user,password,db, keywords,query_log, papers_list, authors_list, relations_list,references_to_db):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,      # <-- Cambia esto
            password=password,  # <-- Cambia esto
            database=db,
            port=port
        )
        cursor = conn.cursor()
        # 1. Insertar Keywords (Si no existen) y obtener sus IDs para el resto del proceso
        keyword_ids = []
        for kw in keywords:
            # Insertar si no existe
            cursor.execute("INSERT IGNORE INTO keywords (keyword) VALUES (%s)", (kw.lower(),))
            # Obtener el ID (ya sea el nuevo o el existente)
            cursor.execute("SELECT id FROM keywords WHERE keyword = %s", (kw.lower(),))
            keyword_ids.append(cursor.fetchone()[0])

        # 2. Insertar en query_logs
        log_sql = """INSERT INTO query_logs 
                     (log_id, fecha_consulta, keywords, start_year, end_year, total_resultados, query_text) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(log_sql, query_log)
        
        query_db_id = query_log[0] # El log_id (uuid) autogenerado
        
        for kw_id in keyword_ids:
            cursor.execute("INSERT INTO query_keywords (query_log_id, keyword_id) VALUES (%s, %s)", 
                           (query_db_id, kw_id))


        # 3. Insertar en query_details (Papers)
        # Usamos IGNORE para no fallar si el paper ya existe de una consulta previa
        paper_sql = "INSERT IGNORE INTO query_details (eid, log_id,title, citations, url) VALUES (%s, %s,%s, %s, %s)"
        cursor.executemany(paper_sql, papers_list)

        # 4. Insertar Autores (Solo si no existen)
        author_sql = "INSERT IGNORE INTO authors (author_id, name) VALUES (%s, %s)"
        cursor.executemany(author_sql, authors_list)

        # 5. Insertar Relaciones Paper-Autor
        rel_sql = "INSERT IGNORE INTO paper_authors (eid, author_id) VALUES (%s, %s)"
        cursor.executemany(rel_sql, relations_list)

        refs_sql = """
        INSERT IGNORE INTO paper_references 
        (source_eid, ref_id, ref_title, ref_authors, ref_url) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(refs_sql, references_to_db)

        conn.commit()
        print(f"✓ Datos guardados exitosamente en MySQL (Log: {query_log[0]})")

    except Error as e:
        print(f"Error conectando a MySQL: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()