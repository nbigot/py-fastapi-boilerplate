from typing import List, Tuple


def query_get_list_of_tables(limit: int) -> Tuple[str, List]:
    query = """
        SELECT
            oid as "table_id",
            relname as "table_name"
        FROM
            pg_class
        LIMIT
            %s
    """
    params = [limit]
    return query, params
