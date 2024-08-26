# -*- coding: utf-8 -*-
# flake8: noqa

import os

import pytest

from app.misc.utils import load_settings

PYTEST_OPTION_CONFIG_FILE_NAME = "config-file-name"

_config_file: str = ""
_config: dict = {}
_root_dir: str = ""


def pytest_addoption(parser):
    # Add an option to choose the yaml configuration file for running tests.
    #
    # Possible values:
    #
    #   "config-test-unit.yaml" for unit tests
    #   "config-test-integration.yaml" for integration tests
    #
    # The default value is integration config file because by default all
    # tests will be run (unit tests + integration tests), so some real servers
    # values are needed to execute integration tests with success.
    #
    # example: of usage:
    # --config-file-name "config-test-integration.yaml"
    #
    #
    # Run only integration tests using a specific config file
    #   this config file contains real values
    #   (uri, fqdn, ip addresses, login, pass, ..)
    #   it targets the test database(s) in order to make real requests
    #
    # -m "integration" --config-file-name "config-test-integration.yaml"
    #
    #
    # Run only unit tests using a specific config file
    #   this config is safe for testing, it can't read/write anything real.
    #   this config file contains only fake values
    #   (uri, fqdn, ip addresses, login, pass, ..)
    #   it targets no database(s), therefore any sql/broadworks request
    #   would fail, it needs to mock any call to databases
    #
    # -m "unittest" --config-file-name "config-test-unit.yaml"
    parser.addoption(
        "--" + PYTEST_OPTION_CONFIG_FILE_NAME,
        action="store",
        default="config-test-unit.yaml",
    )


def pytest_configure(config):  # NOQA
    global _config_file, _config, _root_dir
    _root_dir = config.rootdir

    # register an additional marker(s)
    # config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "unittest: unit tests")

    # retrieve yaml configuration filename for pytest option parameter
    config_file_name = config.option.config_file_name
    _config_file = str(os.path.join(config.rootdir, "tests", "resources", config_file_name))
    assert os.path.isfile(_config_file)
    _config = load_settings(_config_file)


@pytest.fixture(scope="module")
def yaml_config_file() -> str:
    """Get yaml configuration file for testing"""
    return _config_file


@pytest.fixture(scope="module")
def mock_config():
    """Get configuration dict for testing"""
    return _config
