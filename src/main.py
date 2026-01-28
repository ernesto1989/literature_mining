# Literature mining proyect
#
# Minería de literatura científica para la extracción de información relevante.
# Ernesto Cantú
# Monterrey, México
# 26 Enero 2026


from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import pybliometrics.scopus as sc

from dotenv import load_dotenv
import os


def main():

    #Configs scopus
    sc.init()

    query = (
        '(TITLE("xai") and TITLE("business") OR ABS("xai") and ABS("business")) '
        'AND PUBYEAR > 2020  AND PUBYEAR < 2025 '
        'AND DOCTYPE("ar")'
    )

    s = ScopusSearch(query,subscriber=False) 
    print(s.get_results_size())

    print(f"\n📊 Resultados: {s.get_results_size()}")

    for r in s.results:
        print(f"- {r.title} | citas: {r.citedby_count}")


if __name__ == "__main__":
    main()

    
    
    
    
    