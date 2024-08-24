from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    message: Optional[str] = None
