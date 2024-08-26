# pylint: disable=E0213,E1102,W0718
import logging

from fastapi import Request

from app.client.auth_client import AuthClient
from app.client.db_client import DBClient
from app.exception import AppException
from app.misc.permissions_checker import check_demo_permissions
from app.router.default.models import ApiV1ListTablesResponse, ApiV1RequestListTables


class ServiceManager:
    def __init__(self, config: dict, auth_client: AuthClient):
        self.config = config
        self.logger = logging.getLogger("app")
        self.auth_client = auth_client
        self.db_client = DBClient(config=config)

    def handle_errors_decorator(method):
        def inner(self, *args, **kwargs):
            req = kwargs["req"]
            request_type = req.__class__.__name__
            try:
                # TODO: disconnect from database if connected
                return method(self, *args, **kwargs)  # noqa
            except AppException as ex:
                ex.request_type = request_type
                ex.request = req.dict()
                raise ex
            except Exception as ex:
                self.logger.exception(
                    msg="An error occurred",
                    extra={"request_type": request_type, "request": req.dict()},
                )
                raise ex
            finally:
                pass  # disconnect from database if connected

        return inner

    @handle_errors_decorator
    def list_tables(
        self,
        *,
        req: ApiV1RequestListTables,
        request: Request,
    ) -> ApiV1ListTablesResponse:
        # This is a demo method
        check_demo_permissions(
            request=request,
            operation_id="ListTables",
        )
        limit = req.limit if req.limit > 0 else 1
        # result = ApiV1ListTablesResponse(tables=[Table(tableId=i, tableName=f"table{i}") for i in range(limit)])
        result = self.db_client.get_list_of_tables(limit=limit)
        self.logger.info(
            msg="list tables",
            extra={
                "request": request,
                "count": len(result.tables),
            },
        )
        return result
