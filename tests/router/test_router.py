# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.router.default.models import ApiV1GetDateResponse


@pytest.fixture(scope="module")
def client(yaml_config_file):
    os.environ["CONFIG_FILENAME"] = yaml_config_file
    with TestClient(app) as c:
        yield c


@freeze_time("2023-01-01")
def test_get_date(client):
    response = client.get("/demo-project/api/v1/demo/date/")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert data["date"] == "2023-01-01T00:00:00"
    now = ApiV1GetDateResponse(date=datetime.now())
    assert json.dumps(data).replace(" ", "") == now.model_dump_json()
