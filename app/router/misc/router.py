from fastapi import APIRouter, status
from fastapi.responses import FileResponse, RedirectResponse

from app.misc.constants import ROOT_PATH
from app.router.misc.models import HealthCheck

router = APIRouter()


@router.get("/", include_in_schema=False)
@router.get(f"{ROOT_PATH}/", include_in_schema=False)
async def home():
    return RedirectResponse(f"{ROOT_PATH}/docs#")


@router.get("/favicon.ico", include_in_schema=False)
@router.get(f"{ROOT_PATH}/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/html/favicon.ico")


@router.get(
    "/_/status",
    tags=["Misc"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
    include_in_schema=False,
)
@router.get(
    f"{ROOT_PATH}/_/status",
    tags=["Misc"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
    include_in_schema=False,
)
@router.get(
    "/healthcheck",
    tags=["Misc"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
    include_in_schema=False,
)
@router.get(
    f"{ROOT_PATH}/healthcheck",
    tags=["Misc"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def healthcheck() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")
