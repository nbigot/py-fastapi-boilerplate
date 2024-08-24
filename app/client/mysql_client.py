# -*- coding: utf-8 -*-
# pylint: disable=W0401,W0614,W0718
# from datetime import date
# from json import loads
# from typing import List, Optional
# from uuid import UUID, uuid4

# from pymysql.cursors import SSCursor, SSDictCursor
from app.db.mysql.connection import MySQLConnection, MySQLConnectionArgs
from app.exception import AppDBRetryableError
from app.misc.retry import retry
from app.router.default.models import ApiV1ListTablesResponse, Table


class MySQLClient(MySQLConnection):
    def __init__(self, cnx_args: MySQLConnectionArgs, logger, dry_run: bool = False):
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
        # sql_query, sql_args = query_get_list_of_tables(limit)
        # rows = self.select(sql_query, sql_args, False, SSDictCursor)
        # tables = [Table(**row) for row in rows]
        # return ApiV1ListTablesResponse(tables=tables)

        # This is a demo code
        tables = [Table(tableId=i, tableName=f"table{i}") for i in range(limit)]
        return ApiV1ListTablesResponse(tables=tables)
