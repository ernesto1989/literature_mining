#
# Salida a SQLite para realizar mayor análisis relacionales en el futuro.
#
# Ernesto Cantú
# 4 de febrero de 2026
#

import mysql
from mysql.connector import Error


#     

def save_to_db(host,port,user,password,db,query_log, papers_list, authors_list, relations_list):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,      # <-- Cambia esto
            password=password,  # <-- Cambia esto
            database=db,
            port=port
        )
        cursor = conn.cursor()

        # 1. Insertar en query_logs
        log_sql = """INSERT INTO query_logs 
                     (log_id, fecha_consulta, keywords, start_year, end_year, total_resultados, query_text) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(log_sql, query_log)

        # 2. Insertar en query_details (Papers)
        # Usamos IGNORE para no fallar si el paper ya existe de una consulta previa
        paper_sql = "INSERT IGNORE INTO query_details (eid, title, citations, url) VALUES (%s, %s, %s, %s)"
        cursor.executemany(paper_sql, papers_list)

        # 3. Insertar Autores (Solo si no existen)
        author_sql = "INSERT IGNORE INTO authors (author_id, name) VALUES (%s, %s)"
        cursor.executemany(author_sql, authors_list)

        # 4. Insertar Relaciones Paper-Autor
        rel_sql = "INSERT IGNORE INTO paper_authors (eid, author_id) VALUES (%s, %s)"
        cursor.executemany(rel_sql, relations_list)

        conn.commit()
        print(f"✓ Datos guardados exitosamente en MySQL (Log: {query_log[0]})")

    except Error as e:
        print(f"Error conectando a MySQL: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()