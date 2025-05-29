import os

import pytest

from configmanager.configmanager import ConfigManager
from configmanager.source import DictConfigSource

basic_config_path = os.path.join(
    os.path.dirname(__file__), 'basic.yml'
)

def test_configmanager_initialization():
    manager = ConfigManager(basic_config_path=basic_config_path)
    assert manager._basic_config_path == basic_config_path, "Basic config path should be set correctly"
    assert isinstance(
        manager._config, list), "Config should be initialized as a list"


def test_configmanager_load_basic_config():
    manager = ConfigManager(basic_config_path=basic_config_path)
    assert len(manager._config) > 0, "Basic config should be loaded"
    assert manager.get("sample_value") == "Hello, World!", "Default value should match"


def test_configmanager_add_source():
    manager = ConfigManager()
    source = DictConfigSource({"sample_value": "test_value"})
    manager.add_source(source)
    assert source in manager._sources, "Source should be added to the sources list"


def test_configmanager_get():
    manager = ConfigManager(basic_config_path=basic_config_path)
    value = manager.get("sample_value")
    assert value == "Hello, World!", "Value should be retrievable for an existing parameter"


def test_configmanager_key_error():
    manager = ConfigManager(basic_config_path=basic_config_path)
    with pytest.raises(KeyError, match="Configuration key 'non_existent_key' not found."):
        manager.get("non_existent_key")
