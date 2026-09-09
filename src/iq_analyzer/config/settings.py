"""Configuration settings management."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import copy


DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"


class Settings:
    """Configuration settings manager."""

    _instance: Optional["Settings"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config:
            self.load_default()

    def load_default(self) -> None:
        """Load default configuration from YAML file."""
        if DEFAULT_CONFIG_PATH.exists():
            with open(DEFAULT_CONFIG_PATH, "r") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}

    def load_from_file(self, path: Path) -> None:
        """Load configuration from a YAML file."""
        with open(path, "r") as f:
            loaded = yaml.safe_load(f) or {}
        self._config = self._deep_merge(self._config, loaded)

    def load_from_dict(self, config: Dict[str, Any]) -> None:
        """Load configuration from a dictionary."""
        self._config = self._deep_merge(self._config, config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'fft.size')."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return copy.deepcopy(self._config.get(section, {}))

    def to_dict(self) -> Dict[str, Any]:
        """Return a deep copy of the entire configuration."""
        return copy.deepcopy(self._config)

    def save(self, path: Path) -> None:
        """Save current configuration to a YAML file."""
        with open(path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

    @staticmethod
    def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = copy.deepcopy(base)
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Settings._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result


# Global settings instance
settings = Settings()