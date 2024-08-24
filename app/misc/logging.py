# -*- coding: utf-8 -*-
# pylint: disable=W0237

import json
import logging
import logging.config
from datetime import date, datetime
from uuid import UUID

from pythonjsonlogger import jsonlogger

from app.exception import AppException


class EndpointLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if (
            record.args
            and len(record.args) >= 3
            and record.args[2]
            in [
                "/_/status",
                "/healthcheck",
                "/favicon.ico",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/mainroute/_/status",  # TODO: change mainroute to your route
                "/mainroute/healthcheck",
                "/mainroute/favicon.ico",
                "/mainroute/docs",
                "/mainroute/redoc",
                "/mainroute/openapi.json",
            ]
        ):
            return False

        if isinstance(record.exc_info, tuple) and isinstance(record.exc_info[1], AppException):
            # Do not log AppException because they are already logged
            return False

        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    static_fields = {}

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        for key, value in CustomJsonFormatter.static_fields.items():
            log_record[key] = value


class DockerJsonFormatter(CustomJsonFormatter):
    def __init__(self, *_args, **kwargs):
        super().__init__("%(timestamp) %(level) %(name) %(message)", **kwargs)


class ApacheFormatter(logging.Formatter):
    def __init__(self, *_args, **_kwargs):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt=None,
            style="%",
        )


class RichTextFormatter(DockerJsonFormatter):
    def __init__(self, *_args, **kwargs):
        self.fields_separator = kwargs.pop("fieldsSeparator", " - ")
        super().__init__(**kwargs)

    def format(self, record):
        s = super().format(record)
        data = json.loads(s)
        kvl = [f"{key}: {value}" for key, value in data.items()]
        return self.fields_separator.join(kvl)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom Json Encode that also handle special types"""

    @staticmethod
    def _encode(obj):
        if isinstance(obj, dict):

            def transform_type(o):
                if isinstance(o, datetime):
                    return o.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(o, date):
                    return o.strftime("%Y-%m-%d")
                if isinstance(o, UUID):
                    return str(o)
                if isinstance(o, set):
                    return list(o)

                return o

            return {transform_type(k): transform_type(v) for k, v in obj.items()}

        return obj

    def encode(self, obj):
        return super().encode(self._encode(obj))

    def default(self, o):
        if isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%dT%H:%M:%SZ")
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, set):
            return list(o)

        return json.JSONEncoder.default(self, o)


def init_loggers(config: dict) -> None:
    """Initialize loggers"""
    if "logging" in config:
        logging.config.dictConfig(config["logging"])
    else:
        logging.config.dictConfig(config)

    # Add filter to the logger
    logging.getLogger("uvicorn.access").addFilter(EndpointLogFilter())
    logging.getLogger("uvicorn.error").addFilter(EndpointLogFilter())
