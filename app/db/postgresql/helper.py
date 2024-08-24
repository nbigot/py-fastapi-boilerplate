# -*- coding: utf-8 -*-

from typing import List, Optional

import psycopg2


def get_postgresql_cnx(config: dict):
    return psycopg2.connect(
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
        database=config["database"],
    )


def sql_select(
    connection,
    sql_req: str,
    params: Optional[List] = None,
    auto_close: bool = True,
    cursor_args: dict = None,
    auto_reconnect: bool = True,
    retry_count: int = 3,
):
    try:
        if cursor_args is None:
            cursor_args = {}

        with connection.cursor(**cursor_args) as cursor:
            cursor.execute(sql_req, params)
            return cursor.fetchall()
    except psycopg2.OperationalError:
        # force close connection
        connection.close()
        if auto_reconnect and retry_count > 0:
            # reconnect
            connection.ping(reconnect=True)
            return sql_select(
                connection,
                sql_req,
                params,
                auto_close,
                cursor_args,
                auto_reconnect=True,
                retry_count=retry_count - 1,
            )

        raise
    finally:
        if auto_close:
            connection.close()


def sql_execute(
    connection,
    sql_req: str,
    params: Optional[List] = None,
    auto_close: bool = True,
    commit: bool = True,
    cursor_args: dict = None,
    auto_reconnect: bool = True,
    retry_count: int = 3,
):
    try:
        if cursor_args is None:
            cursor_args = {}

        with connection.cursor(**cursor_args) as cursor:
            if params is None:
                params = []
            result = cursor.execute(sql_req, params)
            if commit:
                connection.commit()

            return result
    except psycopg2.OperationalError:
        if (
            auto_reconnect and retry_count > 0
            # and ex.args[0] in POSTGRESQL_RECOVERABLE_ERRORS
        ):
            # reconnect
            connection.ping(reconnect=True)
            return sql_execute(
                connection=connection,
                sql_req=sql_req,
                params=params,
                auto_close=auto_close,
                commit=commit,
                cursor_args=cursor_args,
                auto_reconnect=True,
                retry_count=retry_count - 1,
            )

        raise
    finally:
        if auto_close:
            connection.close()
