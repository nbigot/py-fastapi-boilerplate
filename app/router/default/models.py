from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field, conint


class ApiV1RequestListTables(BaseModel):
    limit: Optional[conint(ge=1, le=1000)] = (Query(1, alias="limit"),)


class Table(BaseModel):
    id: Optional[int] = Field(None, example=1234, alias="tableId")
    name: Optional[str] = Field(
        None,
        example="my_table_name",
        alias="tableName",
    )


class ApiV1ListTablesResponse(BaseModel):
    tables: Optional[list[Table]] = Field(None, example=[Table(id=1234, name="my_table_name")])


class ApiV1GetDateResponse(BaseModel):
    date: datetime = Field(..., example=datetime.now())
