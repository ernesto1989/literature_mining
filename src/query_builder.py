#
# Script que construye las consultas en base a las keywords y parámetros proporcionados.
# 
# Ernesto Cantú
# 04 de febrero de 2026
#

def build_scopus_query(
    keywords,
    year_from=None,
    year_to=None,
    doctype=["ar","jo","su"]
):
    """
    Construye un query Scopus en base a las keywords y parámetros proporcionados.
    """

    if not keywords:
        raise ValueError("Se requiere al menos una keyword")

    keyword_blocks = []

    for kw in keywords:
        kw = kw.strip()
        block = (
            f'(TITLE("{kw}") OR ABS("{kw}") OR KEY("{kw}"))'
        )
        keyword_blocks.append(block)

    query = " AND ".join(keyword_blocks)

    if year_from and year_to:
        query += f" AND PUBYEAR > {year_from - 1} AND PUBYEAR < {year_to + 1}"
    elif year_from:
        query += f" AND PUBYEAR > {year_from - 1}"
    elif year_to:
        query += f" AND PUBYEAR < {year_to + 1}"

    query += " AND ("
    query += " OR ".join([f'DOCTYPE("{dt}")' for dt in doctype])
    query += ")"
    
    return query