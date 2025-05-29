import argparse
import os
from abc import ABC, abstractmethod
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


class ConfigSource(ABC):
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load configuration from the source."""
        raise NotImplementedError


class FileConfigSource(ConfigSource):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> Dict[str, Any]:
        """Load configuration from a YAML file."""
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, 'r') as file:
            return yaml.safe_load(file) or {}


class EnvConfigSource(ConfigSource):
    def load(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        load_dotenv()

        return dict(os.environ)


class DictConfigSource(ConfigSource):
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def load(self) -> Dict[str, Any]:
        """Load configuration from a dictionary."""
        return self.data


class CliConfigSource(ConfigSource):
    """Get configuration values from command line arguments."""

    def __init__(self, args: argparse.Namespace):
        self._args = args

    def load(self) -> dict:
        """Load configuration from command line arguments."""

        return vars(self._args)
