from app.exception.app import AppException
from app.misc.models import ErrorResponse


class AuthException(AppException):
    # AuthException is a base class for all authentication exceptions
    pass


class AuthHeaderException(AppException):
    def __init__(self, *, message: str):
        super().__init__(
            error=ErrorResponse(code=403, name="AuthHeaderException", message=message),
            status_code=403,
            is_warning=True,
        )


class JWTDecodeException(AuthException):
    def __init__(self, *, message: str):
        super().__init__(
            error=ErrorResponse(code=403, name="JWTDecodeException", message=message),
            status_code=403,
            is_warning=True,
        )


class JWTExpiredSignatureError(AuthException):
    def __init__(self, *, message: str):
        super().__init__(
            error=ErrorResponse(code=403, name="JWTExpiredSignatureError", message=message),
            status_code=403,
            is_warning=True,
        )


class SSOException(AppException):
    def __init__(self, *, message: str):
        super().__init__(
            error=ErrorResponse(code=403, name="SSOException", message=message),
            status_code=403,
        )
