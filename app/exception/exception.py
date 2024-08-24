from app.exception.app import AppException
from app.misc.models import ErrorResponse


class ConfigException(AppException):
    def __init__(self, *, message: str):
        super().__init__(
            error=ErrorResponse(code=500, name="ConfigException", message=message),
            status_code=500,
        )
