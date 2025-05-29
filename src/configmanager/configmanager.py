import argparse
import os
import threading
from typing import Any, List, Literal, Optional

import yaml
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from configmanager.source import CliConfigSource, ConfigSource


class Parameter(BaseModel):
    """Base class for configuration management."""

    name: str = Field(min_length=1)
    description: str = ""
    default: Any = None
    type: Literal["string", "int", "float", "bool"] = "string"
    value: Optional[Any] = Field(
        default_factory=lambda: ..., validate_default=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        return name.lower()

    @field_validator("type")
    @classmethod
    def validate_type(cls, type_value: str) -> str:
        valid_types = ["string", "int", "float", "bool"]
        if type_value.lower() not in valid_types:
            raise ValueError(
                f"Invalid type '{type_value}'. Supported types are {', '.join(valid_types)}.")
        return type_value.lower()

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: Any, info: ValidationInfo) -> Any:
        # typeキーが存在するか確認し、存在しない場合はデフォルト値を使用
        specify_type = info.data.get("type", "string").lower()

        # typeの値が有効かどうかを確認
        valid_types = ["string", "int", "float", "bool"]
        if specify_type not in valid_types:
            raise ValueError(
                f"Invalid type '{specify_type}'. Supported types are {', '.join(valid_types)}.")

        # value の値が指定されていない場合、デフォルト値を使用
        if isinstance(value, type(Ellipsis)):
            value = info.data.get("default")
            if value is None:
                return None

        if specify_type == "string":
            if isinstance(value, str):
                return value
            try:
                return str(value)  # Ensure value is a string
            except ValueError:
                raise ValueError(
                    f"Parameter '{info.data['name']}' must be a string, but got {type(value).__name__}.")

        if specify_type == "int":
            if isinstance(value, int):
                return value
            try:
                return int(value)  # Ensure value is an integer
            except ValueError:
                raise ValueError(
                    f"Parameter '{info.data['name']}' must be an integer, but got {type(value).__name__}.")

        if specify_type == "bool":
            if isinstance(value, bool):
                return value
            # convert string representations of boolean values
            if isinstance(value, str) and value.lower() in ["true", "false", "yes", "no"]:
                return value.lower() in ["true", "yes"]

            raise ValueError(
                f"Parameter '{info.data['name']}' must be a boolean, but got {type(value).__name__}.")

        if specify_type == "float":
            if isinstance(value, float):
                return value
            try:
                return float(value)  # Ensure value is a float
            except ValueError:
                raise ValueError(
                    f"Parameter '{info.data['name']}' must be a float, but got {type(value).__name__}.")

        # typeのバリデーションは validate_type メソッドで行われるため、ここでは不要
        return None


class ConfigManager:
    _instance = None
    _lock = threading.Lock()
    _initialized = False  # インスタンスの初期化が完了したかを示す

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, basic_config_path: str = "basic.yml"):
        if not self._initialized:

            self._basic_config_path = basic_config_path
            self._sources: List[ConfigSource] = []
            self._config: List[Parameter] = self.__load_basic_config(
                basic_config_path)
            self._initialized = True

    def __load_basic_config(self, path: str) -> List[Parameter]:
        """Load basic configuration from a YAML file."""
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Configuration file '{path}' not found.")

        with open(path, 'r') as f:
            configs = yaml.safe_load(f)

        parameters = []
        for config in configs:
            parameters.append(Parameter(**config))

        return parameters

    def add_source(self, source: ConfigSource):
        """Add a configuration source with priority."""
        self._sources.append(source)

    def load(self):
        """Load configuration from all sources with priority."""

        self._config = self.__load_basic_config(self._basic_config_path)

        for source in self._sources:
            data = source.load()
            for key in data:
                self.set(key, data[key])

    def get(self, key: str) -> Any:
        """Get a configuration value."""
        key = key.lower()
        try:
            param = [param for param in self._config if param.name == key][0]
        except IndexError:
            raise KeyError(f"Configuration key '{key}' not found.")

        return param.value

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        key = key.lower()
        try:
            param = [param for param in self._config if param.name == key][0]
        except IndexError:
            raise KeyError(f"Configuration key '{key}' not found.")

        new_data = param.model_dump()
        new_data["value"] = value

        new_param = Parameter(**new_data)
        # Add the new parameter with updated value
        self._config.append(new_param)
        self._config.remove(param)  # Remove the existing old parameter

    def get_cli_args(self, args: List[str] | None = None):
        """Get configuration values from command line arguments."""
        parser = argparse.ArgumentParser()

        type_map = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool
        }

        for param in self._config:
            parser.add_argument(f"--{param.name}", type=type_map[param.type], default=param.value,
                                help=param.description)

        parsed_args = parser.parse_args(args)
        srouce = CliConfigSource(parsed_args)
        self.add_source(srouce)
