# -*- coding: utf-8 -*-
# pylint: disable=W0718,R0912,R0915

import uuid
from typing import List, Union

import psycopg2

from app.db.postgresql.helper import get_postgresql_cnx, sql_execute, sql_select
from app.exception import AppDBConnectionError, AppException


class PostgreSQLConnectionArgs:
    """
    PostgreSQLConnectionArgs is a class which contains parameters
    to connect to a PostgreSQL server.
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
            "user": self.login,
            "password": self.password,
            "host": self.hostname,
            "port": self.tcp_port,
            "database": self.database,
        }


class PostgreSQLConnection:
    def __init__(self, cnx_args: PostgreSQLConnectionArgs, logger):
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
        """Connect to server"""
        try:
            if self.is_alive():
                return

            self.sql_cnx = self.get_postgresql_cnx()
            if not self.is_alive():
                raise AppDBConnectionError(message="Can't connect to PostgreSQL (not alive)")
        except psycopg2.Error as ex:
            raise AppDBConnectionError(message="Can't connect to PostgreSQL", ex=ex) from ex
        except Exception:
            self.disconnect()
            raise

    def get_postgresql_cnx(self):
        return get_postgresql_cnx(self._cnx_args.as_dict)

    def disconnect(self) -> None:
        """Disconnect form server"""
        if self.sql_cnx:
            try:
                #  saw behaviour when it failed to send logout cmd due
                #  Broken Pipe assuming that session will be closed with
                #  closed socket
                #  ignore Broken Pipes and other socket issue not interesting in
                #  them because server could close socket after LogoutRequest
                #  was sent
                if not self.sql_cnx.closed:
                    self.sql_cnx.close()
            except (
                IOError,
                EOFError,
                BrokenPipeError,
                psycopg2.Error,
                AppDBConnectionError,
            ):
                pass
            finally:
                self.sql_cnx = None

    def is_alive(self) -> bool:
        """Check if connexion is alive"""
        if not self.sql_cnx:
            return False
        try:
            result = self.select(sql_req="SELECT 1", auto_close=False)
            if result != [(1,)]:
                raise ValueError("SQL Alive check: invalid response")

            return True
        except (IOError, EOFError, ValueError, BrokenPipeError, psycopg2.Error):
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
        cursor_args: dict = None,
    ) -> List[Union[dict, tuple]]:
        try:
            return sql_select(self.cnx, sql_req, params, auto_close, cursor_args)
        except AppException as ex:
            ex.log_exception()
            raise ex

    def execute(
        self,
        sql_req: str,
        params=None,
        auto_close: bool = True,
        commit: bool = True,
        cursor_args: dict = None,
    ):
        return sql_execute(
            connection=self.cnx,
            sql_req=sql_req,
            params=params,
            auto_close=auto_close,
            commit=commit,
            cursor_args=cursor_args,
        )

    # def safe_select(
    #     self, sql_req: str, params: List, cursor_class: Type[Cursor] = Cursor
    # ) -> Any:
    #     cursor = None
    #     if params is None:
    #         params = []
    #
    #     try:
    #         connection = self.cnx
    #         cursor = connection.cursor(cursor_class)
    #         cursor.execute(sql_req, params)
    #         result = cursor.fetchall()
    #         cursor.close()
    #         return result
    #     except Exception as ex:
    #         mysql_error_code = None
    #         try:
    #             if isinstance(ex, pymysql.err.Error) and ex.args:
    #                 mysql_error_code = ex.args[0]
    #         except Exception:
    #             pass
    #
    #         self.logger.error(
    #             str(ex),
    #             extra={
    #                 "sql_request": sql_req,
    #                 "sql_params": str(params),
    #                 "mysql_error_code": mysql_error_code,
    #             },
    #         )
    #
    #         try:
    #             if cursor:
    #                 cursor.close()
    #         except Exception:
    #             pass
    #         finally:
    #             del cursor
    #
    #         try:
    #             self.disconnect()
    #         except Exception:
    #             pass
    #
    #         if mysql_error_code in MYSQL_RECOVERABLE_ERRORS:
    #             raise AppDBRetryableError(
    #                 message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
    #                 error_code=mysql_error_code,
    #                 ex=ex,
    #                 error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
    #             ) from ex
    #
    #         if (
    #             isinstance(ex, pymysql.err.Error)
    #             or str(ex.__class__) == "<class 'pymysql.err.MySQLError'>"
    #         ):
    #             # do not retry on this kind of error
    #             raise AppDBError(
    #                 message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
    #                 error_code=mysql_error_code,
    #                 ex=ex,
    #                 error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
    #                 is_permanent_error=False,
    #             ) from ex
    #
    #         raise AppException(message=str(ex), error_type=str(type(ex)), ex=ex) from ex
    #
    # def safe_execute(
    #     self,
    #     sql_req: str,
    #     params: Optional[Union[List, Dict]] = None,
    #     commit: bool = True,
    #     auto_close: bool = True,
    #     cursor_class: Type[Cursor] = Cursor,
    # ) -> Tuple[int, Any]:
    #     connection = None
    #     cursor = None
    #     if params is None:
    #         params = []
    #
    #     try:
    #         number_of_affected_rows = 0
    #         connection = self.cnx
    #         cursor = connection.cursor(cursor_class)
    #         try:
    #             number_of_affected_rows = cursor.execute(sql_req, params)
    #         except pymysql.err.Warning as ex:
    #             self.logger.warning(
    #                 str(ex), extra={"sql_request": sql_req, "sql_params": str(params)}
    #             )
    #
    #         try:
    #             last_row_id = cursor.lastrowid
    #         except Exception:
    #             last_row_id = None
    #
    #         try:
    #             if cursor and auto_close:
    #                 cursor.close()
    #
    #             if commit:
    #                 connection.commit()
    #         except Exception:
    #             pass
    #
    #         return number_of_affected_rows, last_row_id
    #     except Exception as ex:
    #         mysql_error_code = None
    #         try:
    #             if isinstance(ex, pymysql.err.Error) and ex.args:
    #                 mysql_error_code = ex.args[0]
    #         except Exception:
    #             pass
    #
    #         self.logger.error(
    #             str(ex),
    #             extra={
    #                 "sql_request": sql_req,
    #                 "sql_params": str(params),
    #                 "mysql_error_code": mysql_error_code,
    #             },
    #         )
    #
    #         try:
    #             if cursor:
    #                 cursor.close()
    #         except Exception:
    #             pass
    #
    #         try:
    #             if connection:
    #                 connection.rollback()
    #         except Exception:
    #             pass
    #
    #         try:
    #             self.disconnect()
    #         except Exception:
    #             pass
    #
    #         if mysql_error_code in MYSQL_RECOVERABLE_ERRORS:
    #             raise AppDBRetryableError(
    #                 message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
    #                 error_code=mysql_error_code,
    #                 ex=ex,
    #                 error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
    #             ) from ex
    #
    #         if (
    #             isinstance(ex, pymysql.err.Error)
    #             or str(ex.__class__) == "<class 'pymysql.err.MySQLError'>"
    #         ):
    #             # do not retry on this kind of error
    #             # example: 1062 duplicate entry error
    #             raise AppDBError(
    #                 message=ERROR_CANNOT_EXECUTE_MYSQL_COMMAND,
    #                 error_code=mysql_error_code,
    #                 ex=ex,
    #                 error_type=MYSQL_ERRORS.get(mysql_error_code, "MySQLError"),
    #                 is_permanent_error=False,
    #             ) from ex
    #
    #         raise AppException(message=str(ex), error_type=str(type(ex)), ex=ex) from ex

    def rollback(self):
        self.cnx.rollback()

    def commit(self):
        self.cnx.commit()
