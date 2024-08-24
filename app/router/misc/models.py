from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Response when performing a health check"""

    status: str = "OK"
