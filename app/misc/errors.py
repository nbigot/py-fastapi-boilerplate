from typing import Optional

from fastapi.responses import JSONResponse

from app.misc.models import ErrorResponse


class ResponseNotImplementedError(ErrorResponse):
    code: Optional[str] = "500"
    name: Optional[str] = "NotImplementedError"
    message: Optional[str] = "This route is not implemented yet"


HTTP_NotImplementedError = JSONResponse(status_code=500, content=ResponseNotImplementedError().dict())
