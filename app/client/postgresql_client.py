# -*- coding: utf-8 -*-
# pylint: disable=W0401,W0614,W0718
# from datetime import date
# from json import loads
# from typing import List, Optional
# from uuid import UUID, uuid4

from app.db.postgresql.connection import PostgreSQLConnection, PostgreSQLConnectionArgs
from app.exception.db import AppDBRetryableError
from app.misc.retry import retry
from app.router.default.models import ApiV1ListTablesResponse, Table
from app.sql.queries import query_get_list_of_tables


class PostgreSQLClient(PostgreSQLConnection):
    def __init__(self, cnx_args: PostgreSQLConnectionArgs, logger, dry_run: bool = False):
        self.dry_run = dry_run
        super().__init__(cnx_args=cnx_args, logger=logger)

    # This is a demo method
    @retry(exceptions=(AppDBRetryableError,), tries=4, delay=1, max_delay=4, backoff=2)
    def get_list_of_tables(
        self,
        limit: int,
    ) -> ApiV1ListTablesResponse:
        # The commented code below is a placeholder for the actual code that will be implemented
        #
        sql_query, sql_args = query_get_list_of_tables(limit)
        rows = self.select(sql_query, sql_args, auto_close=False, cursor_args={})
        tables = [Table(tableId=tableId, tableName=tableName) for tableId, tableName in rows]
        return ApiV1ListTablesResponse(tables=tables)

        # This is a demo code
        # tables = [Table(tableId=i, tableName=f"table{i}") for i in range(limit)]
        # return ApiV1ListTablesResponse(tables=tables)
