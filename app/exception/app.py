# -*- coding: utf-8 -*-

import logging
from typing import Optional
from uuid import uuid4

from fastapi.responses import JSONResponse

from app.misc.models import ErrorResponse


class AppException(Exception):
    """Base class for exception handling"""

    def __init__(
        self,
        message: str = "",
        error_type: str = "",
        error: Optional[ErrorResponse] = None,
        status_code: int = 500,
        ex: Exception = None,
        logger_name: str = "app",
        is_warning: bool = False,
    ):
        super().__init__()
        self.is_warning = is_warning
        self.logger_name = logger_name
        self.exception_unique_id = str(uuid4())
        self.ex = ex
        if error:
            self.message = error.message
            self.error_type = error.name
            self.status_code = status_code or error.code
            self.error = error
        else:
            self.message = message
            self.error_type = error_type
            self.status_code = status_code
            self.error = ErrorResponse(code=str(status_code), name=error_type, message=message)

    @property
    def logger(self) -> logging.Logger:
        """
        Get the exception logger.

        :return: logging.Logger
        """
        return logging.getLogger(self.logger_name)

    def log_exception(self) -> None:
        """
        Log the current exception.

        :return: None
        """
        if self.is_warning:
            self.logger.warning(msg=str(self), extra={"error": self.to_json()})
        else:
            self.logger.exception(msg=str(self), extra={"error": self.to_json()})

    def to_json(self) -> dict:
        return {
            "id": self.exception_unique_id,
            "class": self.__class__.__name__,
            "message": self.message,
            "type": self.error_type,
            "ex": str(self.ex),
        }

    def to_json_response(self):
        return JSONResponse(status_code=self.status_code, content=self.error.dict())

    def to_error_response(self) -> ErrorResponse:
        return self.error

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}: id: [{self.exception_unique_id}] "
            f"error_type: [{self.error_type}] "
            f"message: [{self.message}] ex: [{self.ex}]"
        )
