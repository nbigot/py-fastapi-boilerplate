# -*- coding: utf-8 -*-
import io
import json
import os
from datetime import datetime, timezone
from logging import getLogger
from typing import Any, Optional
from uuid import UUID

import boto3
import jinja2
from yaml import unsafe_load

from app.exception import ConfigException
from app.misc.constants import AWS_ECS_ENV_KEY
from app.misc.logging import init_loggers


def get_config_path() -> str:
    """Return the path of the configuration file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")


def load_settings(filename: str) -> dict:
    """Load the application settings."""

    def load_jinja_template(jinja_filepath: str) -> str:
        # Render Jinja configuration template
        # (convert_payload_to_enum_record variables with env vars)
        with open(file=os.path.realpath(jinja_filepath), mode="r", encoding="utf-8") as fd:
            data = fd.read()
            template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(data)
            return template.render(env=os.environ)

    # Load yaml configuration into variable
    return unsafe_load(io.StringIO(load_jinja_template(filename)))


def load_json_schema(filename: str) -> dict:
    """Load the json validation schema."""
    with open(file=filename, mode="r", encoding="utf-8") as fd:
        return json.load(fd)


def now_iso8601() -> str:
    """Return the current datetime."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def initial_config_verifications(config: dict) -> None:
    """Perform initial configuration verifications."""
    logger = getLogger("app")

    # Customize the configuration verification here
    # example:
    #
    # if not config["section1"]["parameter1"]:
    #     message = "Missing parameter1 value in the configuration file"
    #     logger.error(message)
    #     raise ConfigException(message=message)

    if config["auth"]["basic"]["enable"] is True and not config["auth"]["basic"]["password"]:
        message = "Missing password value in the configuration file for auth basic"
        logger.error(message)
        raise ConfigException(message=message)


def set_environment_variables_from_aws_secret() -> None:
    """Set environment variables from AWS secret."""
    for env_key in AWS_ECS_ENV_KEY:
        envs = json.loads(os.environ.get(env_key, "{}"))
        for key, value in envs.items():
            os.environ[key] = value


def setup() -> dict:
    set_environment_variables_from_aws_secret()
    config_filename = os.getenv("CONFIG_FILENAME", "app/config/config.yaml")
    config = load_settings(config_filename)
    init_loggers(config)
    initial_config_verifications(config=config)
    if config["aws"].get("profile_name"):
        boto3.setup_default_session(profile_name=config["aws"]["profile_name"])

    return config


def to_uuid(uuid_value: Any) -> Optional[UUID]:
    """Convert a string to a UUID."""
    if not uuid_value:
        return None

    if isinstance(uuid_value, str):
        return UUID(uuid_value)

    if isinstance(uuid_value, UUID):
        return uuid_value

    if isinstance(uuid_value, int):
        return UUID(int=uuid_value)

    raise ValueError(f"Invalid UUID string: {uuid_value}")
