# -*- coding: utf-8 -*-
# pylint: disable=W0718,R0912,R0915

import uuid
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import pymysql
from pymysql.cursors import Cursor
from pymysql.err import OperationalError

from app.db.mysql.helper import get_mysql_cnx, sql_execute, sql_select
from app.exception import AppDBConnectionError, AppDBError, AppDBRetryableError, AppException
from app.exception.mysql import ERROR_CANNOT_EXECUTE_MYSQL_COMMAND, MYSQL_ERRORS, MYSQL_RECOVERABLE_ERRORS


class MySQLConnectionArgs:
    """
    MySQLConnectionArgs is a class which contains parameters
    to connect to a MySQL server.
    """

    def __init__(
        self,
        hostname: str,
        tcp_port: int,
        login: str,
        password: str,
        database: str,
        program: str,
    ):
        self.hostname = hostname
        self.tcp_port = tcp_port
        self.login = login
        self.password = password
        self.database = database
        self.program = program

    @property
    def as_dict(self):
        return {
            "username": self.login,
            "hostname": self.hostname,
            "password": self.password,
            "database": self.database,
            "port": self.tcp_port,
            "program": self.program,
        }


class MySQLConnection:
    def __init__(self, cnx_args: MySQLConnectionArgs, logger):
        self._cnx_args = cnx_args
        self.logger = logger
        self.session_id = str(uuid.uuid1())
        self.sql_cnx = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        self.disconnect()

    def connect(self) -> None:
        """Connect to a mysql server"""
        try:
            if self.is_alive():
                return

            self.sql_cnx = self.get_mysql_cnx()
            assert self.is_alive()
        except OperationalError as ex:
            raise AppDBConnectionError("Can't connect to MySql", ex=ex) from ex
        except Exception:
            self.disconnect()
            raise

    def get_mysql_cnx(self):
        return get_mysql_cnx(self._cnx_args.as_dict)

    def disconnect(self) -> None:
        """Disconnect form a mysql server"""
        if self.sql_cnx:
            try:
                #  saw behaviour when it failed to send logout cmd due
                #  Broken Pipe assuming that session will be closed with
                #  closed socket
                #  ignore Broken Pipes and other socket issue not interesting in
                #  them because server could close socket after LogoutRequest
                #  was sent
                if self.sql_cnx.open:
                    self.sql_cnx.close()
            except (
                IOError,
                EOFError,
                BrokenPipeError,
                OperationalError,
                AppDBConnectionError,
            ):
                pass
            finally:
                self.sql_cnx = None

    def is_alive(self) -> bool:
        """Check if mysql connexion is alive"""
        if not self.sql_cnx:
            return False
        try:
            result = self.select(sql_req="SELECT 1", auto_close=False)
            if result != [{"1": 1}]:
                raise ValueError("SQL Alive check: invalid response")

            return True
        except (IOError, EOFError, ValueError, BrokenPipeError, OperationalError):
            return False

    @property
    def cnx(self):
        if not self.sql_cnx:
            self.connect()

        return self.sql_cnx

    def select(
        self,
        sql_req: str,
        params=None,
        auto_close: bool = True,
        cursor_class: Type[Cursor] = None,
    ) -> List[Union[dict, tuple]]:
        return sql_select(self.cnx, sql_req, params, auto_close, cursor_class)

    def execute(
        self,
        sql_req: str,
        params=None,
        auto_close: bool = True,
        commit: bool = True,
        cursor_class: Type[Cursor] = None,
    ):
        return sql_execute(
            connection=self.cnx,
            sql_req=sql_req,
            params=params,
            auto_close=auto_close,
            commit=commit,
            cursor_class=cursor_class,
        )

    def safe_select(self, sql_req: str, params: List, cursor_class: Type[Cursor] = Cursor) -> Any:
        cursor = None
        if params is None:
            params = []

        try:
            connection = self.cnx
            cursor = connection.cursor(cursor_class)
            cursor.execute(sql_req, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as ex:
            mysql_error_code = None
            try:
                if isinstance(ex, pymysql.err.Error) and ex.args:
                    mysql_error_code = ex.args[0]
            except Exception:
                pass

            self.logger.error(
                str(ex),
                extra={
                    "sql_request": sql_req,
                    "sql_params": str(params),
                    "mysql_error_code": mysql_error_code,
                },
            )

            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
            finally:
                del cursor

            try:
                self.disconnect()
            except Exception:
                pass

            if mysql_error_code in MYSQL_RECOVERABLE_ERRORS:
                raise AppDBRetryableError(
                    message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
                    error_code=mysql_error_code,
                    ex=ex,
                    error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
                ) from ex

            if isinstance(ex, pymysql.err.Error) or str(ex.__class__) == "<class 'pymysql.err.MySQLError'>":
                # do not retry on this kind of error
                raise AppDBError(
                    message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
                    error_code=mysql_error_code,
                    ex=ex,
                    error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
                    is_permanent_error=False,
                ) from ex

            raise AppException(message=str(ex), error_type=str(type(ex)), ex=ex) from ex

    def safe_execute(
        self,
        sql_req: str,
        params: Optional[Union[List, Dict]] = None,
        commit: bool = True,
        auto_close: bool = True,
        cursor_class: Type[Cursor] = Cursor,
    ) -> Tuple[int, Any]:
        connection = None
        cursor = None
        if params is None:
            params = []

        try:
            number_of_affected_rows = 0
            connection = self.cnx
            cursor = connection.cursor(cursor_class)
            try:
                number_of_affected_rows = cursor.execute(sql_req, params)
            except pymysql.err.Warning as ex:
                self.logger.warning(str(ex), extra={"sql_request": sql_req, "sql_params": str(params)})

            try:
                last_row_id = cursor.lastrowid
            except Exception:
                last_row_id = None

            try:
                if cursor and auto_close:
                    cursor.close()

                if commit:
                    connection.commit()
            except Exception:
                pass

            return number_of_affected_rows, last_row_id
        except Exception as ex:
            mysql_error_code = None
            try:
                if isinstance(ex, pymysql.err.Error) and ex.args:
                    mysql_error_code = ex.args[0]
            except Exception:
                pass

            self.logger.error(
                str(ex),
                extra={
                    "sql_request": sql_req,
                    "sql_params": str(params),
                    "mysql_error_code": mysql_error_code,
                },
            )

            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass

            try:
                if connection:
                    connection.rollback()
            except Exception:
                pass

            try:
                self.disconnect()
            except Exception:
                pass

            if mysql_error_code in MYSQL_RECOVERABLE_ERRORS:
                raise AppDBRetryableError(
                    message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
                    error_code=mysql_error_code,
                    ex=ex,
                    error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
                ) from ex

            if isinstance(ex, pymysql.err.Error) or str(ex.__class__) == "<class 'pymysql.err.MySQLError'>":
                # do not retry on this kind of error
                # example: 1062 duplicate entry error
                raise AppDBError(
                    message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
                    error_code=mysql_error_code,
                    ex=ex,
                    error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
                    is_permanent_error=False,
                ) from ex

            raise AppException(message=str(ex), error_type=str(type(ex)), ex=ex) from ex

    def rollback(self):
        self.cnx.rollback()

    def commit(self):
        self.cnx.commit()
