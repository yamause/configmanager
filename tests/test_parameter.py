import logging

import pytest
from pydantic import ValidationError

# from configmanager import ConfigManager
from configmanager import Parameter

logger = logging.getLogger(__name__)


def test_parameter():
    source = {
        "name": "test_param",
        "description": "A test parameter",
        "default": "111",
        "type": "int",
    }
    parameter = Parameter(**source)
    logger.info(parameter)
    assert parameter.name == "test_param", "Parameter name should match"


def test_parameter_invalid_int():
    source = {
        "name": "test_param",
        "description": "A test parameter",
        "default": "bad value",
        "type": "int",
    }

    with pytest.raises(ValueError, match="Parameter 'test_param' must be an integer"):
        parameter = Parameter(**source)
        logger.info(parameter)


def test_parameter_string_type():
    source = {
        "name": "string_param",
        "default": "test_string",
        "type": "string",
    }
    parameter = Parameter(**source)
    assert parameter.value == "test_string", "Value should match the default string"


def test_parameter_bool_type():
    source = {
        "name": "bool_param",
        "default": True,
        "type": "bool",
    }
    parameter = Parameter(**source)
    assert parameter.value is True, "Value should match the default boolean"


def test_parameter_float_type():
    source = {
        "name": "float_param",
        "default": 3.14,
        "type": "float",
    }
    parameter = Parameter(**source)
    assert parameter.value == 3.14, "Value should match the default float"


def test_parameter_invalid_bool():
    source = {
        "name": "invalid_bool",
        "default": "not_a_bool",
        "type": "bool",
    }
    with pytest.raises(ValueError, match="Parameter 'invalid_bool' must be a boolean"):
        Parameter(**source)


def test_parameter_invalid_float():
    source = {
        "name": "invalid_float",
        "default": "not_a_float",
        "type": "float",
    }
    with pytest.raises(ValueError, match="Parameter 'invalid_float' must be a float"):
        Parameter(**source)


def test_parameter_invalid_type():
    source = {
        "name": "invalid_type",
        "default": "default_value",
        "type": "not_a_valid_type",
    }
    with pytest.raises(ValidationError, match="Input should be 'string', 'int', 'float' or 'bool'"):
        Parameter(**source)
