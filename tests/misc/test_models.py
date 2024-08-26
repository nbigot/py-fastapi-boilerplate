# -*- coding: utf-8 -*-
# flake8: noqa

from app.router.misc.models import HealthCheck


def test_healthcheck():
    model = HealthCheck()
    assert model.status == "OK"
