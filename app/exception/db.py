# -*- coding: utf-8 -*-

from app.exception import AppException


class AppDBError(AppException):
    def __init__(
        self,
        message: str = None,
        error_code: int = None,
        error_type: str = "AppDBError",
        ex: Exception = None,
        is_permanent_error: bool = False,
        logger_name: str = "db",
    ):
        super().__init__(message=message, ex=ex, error_type=error_type)
        self.logger_name = logger_name
        self.is_permanent_error = is_permanent_error
        self.error_code = error_code


class AppDBConnectionError(AppDBError):
    def __init__(self, message: str = "", ex: Exception = None, logger_name: str = "db"):
        super().__init__(
            message=message,
            ex=ex,
            error_type="AppDBConnectionError",
            logger_name=logger_name,
        )


class AppDBRetryableError(AppDBError):
    def __init__(
        self,
        message: str = None,
        error_code: int = None,
        error_type: str = "AppDBRetryableError",
        ex: Exception = None,
    ):
        super().__init__(message=message, error_code=error_code, ex=ex, error_type=error_type)
        self.is_permanent_error = False
