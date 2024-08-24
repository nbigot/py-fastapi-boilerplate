# -*- coding: utf-8 -*-

from typing import List, Optional

import pymysql

from app.exception.mysql import MYSQL_RECOVERABLE_ERRORS


def get_mysql_cnx(config: dict):
    return pymysql.connect(
        user=config["username"],
        host=config["hostname"],
        port=config["port"],
        password=config["password"],
        db=config["database"],
        program_name=config["program"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def sql_select(
    connection: pymysql.connections.Connection,
    sql_req: str,
    params: Optional[List] = None,
    auto_close: bool = True,
    cursor_class: pymysql.cursors.Cursor = None,
    auto_reconnect: bool = True,
    retry_count: int = 3,
):
    try:
        with connection.cursor(cursor_class) as cursor:
            if params is None:
                params = []
            cursor.execute(sql_req, params)
            return cursor.fetchall()
    except pymysql.err.InterfaceError:
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
                cursor_class,
                auto_reconnect=True,
                retry_count=retry_count - 1,
            )

        raise
    except pymysql.err.OperationalError as ex:
        # Error Code: 2013 - Lost connection to MySQL server during query:
        # Error Code: 2006 - MySQL server has gone away 'Une connexion existante a dû être fermée par l’hôte distant'
        if ex.args[0] in [2006, 2013] and auto_reconnect and retry_count > 0:
            # reconnect
            connection.ping(reconnect=True)
            return sql_select(
                connection,
                sql_req,
                params,
                auto_close,
                cursor_class,
                auto_reconnect=True,
                retry_count=retry_count - 1,
            )

        raise
    finally:
        if auto_close:
            connection.close()


def sql_execute(
    connection: pymysql.connections.Connection,
    sql_req: str,
    params: Optional[List] = None,
    auto_close: bool = True,
    commit: bool = True,
    cursor_class: pymysql.cursors.Cursor = None,
    auto_reconnect: bool = True,
    retry_count: int = 3,
):
    try:
        with connection.cursor(cursor_class) as cursor:
            if params is None:
                params = []
            result = cursor.execute(sql_req, params)
            if commit:
                connection.commit()

            return result
    except pymysql.err.OperationalError as ex:
        # Error Code: 2013 - Lost connection to MySQL server during query:
        # Error Code: 2006 - MySQL server has gone away 'Une connexion existante a dû être fermée par l’hôte distant'
        # Error Code: 2003 - MySQL network connection has been refused
        if ex.args[0] in MYSQL_RECOVERABLE_ERRORS and auto_reconnect and retry_count > 0:
            # reconnect
            connection.ping(reconnect=True)
            return sql_execute(
                connection=connection,
                sql_req=sql_req,
                params=params,
                auto_close=auto_close,
                commit=commit,
                cursor_class=cursor_class,
                auto_reconnect=True,
                retry_count=retry_count - 1,
            )

        raise
    finally:
        if auto_close:
            connection.close()
