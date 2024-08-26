# pylint: disable=W0613,W0107


from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from fastapi import APIRouter, Depends, Query, Request
from pydantic import conint

from app.misc.constants import ENDPOINT_API_V1
from app.misc.errors import HTTP_NotImplementedError
from app.misc.models import ErrorResponse
from app.misc.permissions_checker import user_is_authenticated
from app.router.default.models import ApiV1GetDateResponse, ApiV1ListTablesResponse, ApiV1RequestListTables

router = APIRouter(prefix=ENDPOINT_API_V1, dependencies=[Depends(user_is_authenticated)])


@router.get(
    "/demo/name/",
    response_model=ApiV1ListTablesResponse,
    responses={
        "400": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
    },
    summary="Return a list of tables",
    operation_id="ListTables",
    tags=["Demo", "Admin"],
)
def list_tables(
    request: Request,
    # body: ApiV1RequestListTables,
    limit: Optional[conint(ge=1, le=1000)] = Query(1, alias="limit"),
) -> Union[ApiV1ListTablesResponse, ErrorResponse]:
    """
    Return a list of French phone numbers
    """
    req = ApiV1RequestListTables(limit=limit)
    return request.app.state.service_manager.list_tables(req=req, request=request)


@router.get(
    "/demo/date/",
    response_model=ApiV1GetDateResponse,
    responses={
        "400": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
    },
    summary="Return the date",
    operation_id="GetDate",
    tags=["Demo"],
)
def get_date() -> Union[ApiV1GetDateResponse, ErrorResponse]:
    """
    Return the date
    """
    return ApiV1GetDateResponse(date=datetime.now())


@router.get(
    "/demo/error/",
    response_model=ErrorResponse,
    responses={
        "500": {"model": ErrorResponse},
    },
    summary="Return an error",
    operation_id="GetError",
    tags=["Demo"],
)
def get_error() -> ErrorResponse:
    """
    Return the date
    """
    return HTTP_NotImplementedError
