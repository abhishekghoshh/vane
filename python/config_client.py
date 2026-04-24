"""Client to load and process YAML configuration files."""

import json
import logging
import os
import re
from typing import Any

import yaml
from pydantic import BaseModel


# Regex patterns for placeholders
env_var_pattern = re.compile(r"\$\{(\w+)}")  # Matches ${ENV_KEY}
env_var_with_default_pattern = re.compile(r"\$\{(\w+):([^}]+)}")  # Matches ${ENV_KEY:DEFAULT_VAL}

logger = logging.getLogger(__name__)


def load_file(file_path: str, default_value: Any = None) -> dict:
    """
    Load a YAML or JSON file and return its contents as a dictionary.
    :param default_value:
    :param file_path:
    :return:
    """
    try:
        if not os.path.isfile(file_path):
            logger.error("File not found: %s", file_path)
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, mode="r", encoding="utf-8") as file:
            if file_path.endswith((".yaml", ".yml")):
                return yaml.safe_load(file)
            if file_path.endswith(".json"):
                return json.load(file)

            logger.error("Unsupported file format: %s", file_path)
            raise ValueError(f"Unsupported file format: {file_path}")
    except Exception as e:
        logger.error("Error loading file %s: %s", file_path, e)
        if default_value is not None:
            return default_value
        raise e


def resolve_placeholders(value: str, default_value: str | None = None, exception_for_none_value: bool = True) -> str:
    """
    Validate and replace environment variable placeholders in the given value.
    :param exception_for_none_value:
    :param default_value:
    :param value:
    :return:
    """
    if not value:
        if exception_for_none_value:
            raise ValueError("Value cannot be None or empty.")
        return default_value

    # Check for ${ENV_KEY:DEFAULT_VAL} pattern
    match_with_default = env_var_with_default_pattern.match(value)
    if match_with_default:
        env_key = match_with_default.group(1)
        default_val = match_with_default.group(2)
        return os.getenv(env_key, default_val)

    # Check for ${ENV_KEY} pattern
    match = env_var_pattern.match(value)
    if match:
        env_key = match.group(1)
        env_value = os.getenv(env_key)
        if env_value is None:
            if default_value is not None:
                return default_value
            raise EnvironmentError(f"Environment variable '{env_key}' not set.")
        return env_value

    # Return the original value if no patterns matched
    return value


def call_if_not_none(obj, func_name, *args, **kwargs):
    """
    Call a function on an object if the object is not None.
    :param obj:
    :param func_name:
    :param args:
    :param kwargs:
    :return:
    """
    if obj is None:
        return None
    func = getattr(obj, func_name)
    return func(*args, **kwargs)


def get_nested_object(obj, dot_separated_keys: str, default_value=None):
    """
    Retrieve a nested object from a dictionary using dot-separated keys.
    :param obj:
    :param dot_separated_keys:
    :param default_value:
    :return:
    """
    keys = dot_separated_keys.split(".")
    current_obj = obj
    for key in keys:
        if isinstance(current_obj, dict):
            current_obj = current_obj.get(key, default_value)
        elif hasattr(current_obj, key):
            current_obj = getattr(current_obj, key)
        else:
            return default_value
    return current_obj


class LggerDetails(BaseModel):
    """
    Logger configuration details.
    """

    format: str | None = None
    default_level: str | None = None
    package_levels: dict[str, str] = {}

    def resolve(self):
        """
        Validate the logger details.
        """
        self.format = resolve_placeholders(
            value=self.format,
            default_value="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            exception_for_none_value=False,
        )
        self.default_level = resolve_placeholders(
            value=self.default_level,
            default_value="INFO",
            exception_for_none_value=False,
        )
        for package, level in self.package_levels.items():
            resolved_level = resolve_placeholders(value=level, default_value="INFO", exception_for_none_value=False)
            self.package_levels[package] = resolved_level


class AppConfigDetails(BaseModel):
    """
    Application configuration details.
    """

    profiles: str | None = None
    static_configs: str | None = None

    def resolve(self):
        """
        Validate the application config details.
        """
        self.profiles = resolve_placeholders(value=self.profiles, default_value="", exception_for_none_value=False)
        self.static_configs = resolve_placeholders(value=self.static_configs, default_value="", exception_for_none_value=False)


class RequestConfigDetails(BaseModel):
    """
    Request configuration details.
    """

    connect_timeout: int | None = None
    read_timeout: int | None = None
    timeout_seconds: int | None = None
    max_retries: int | None = None

    def resolve(self):
        """
        Validate the request config details.
        """
        if self.timeout_seconds is None or self.timeout_seconds <= 0:
            self.timeout_seconds = 30  # default timeout
        if self.max_retries is None or self.max_retries < 0:
            self.max_retries = 3  # default retries
        if self.connect_timeout is None or self.connect_timeout <= 0:
            self.connect_timeout = 5  # default connect timeout
        if self.read_timeout is None or self.read_timeout <= 0:
            self.read_timeout = 15  # default read timeout


class Application(BaseModel):
    """
    Application configuration.
    """

    config: AppConfigDetails | None = None
    request: RequestConfigDetails | None = None
    logger: LggerDetails | None = None

    def resolve(self):
        """
        Validate the application configuration.
        """
        call_if_not_none(self.config, "resolve")
        call_if_not_none(self.request, "resolve")
        call_if_not_none(self.logger, "resolve")


class BootstrapConfig(BaseModel):
    """
    Bootstrap configuration structure.
    """

    application: Application | None = None

    def resolve(self):
        """
        Validate the bootstrap configuration.
        """
        call_if_not_none(self.application, "resolve")


# pylint: disable=too-few-public-methods
class ConfigClient(metaclass=Singleton):
    """
    Client to load and process YAML configuration files.
    """

    def __init__(self, resource_directory: str, bootstrap_config_filename: str):
        self.resource_directory = resource_directory
        self.bootstrap_config_filename = bootstrap_config_filename
        self.bootstrap_config_dict = load_file(os.path.join(self.resource_directory, self.bootstrap_config_filename))
        self.bootstrap_config: BootstrapConfig = BootstrapConfig(**self.bootstrap_config_dict)
        self.bootstrap_config.resolve()
        logger.info("Bootstrap configuration loaded.")
        print(self.bootstrap_config)
        self.additional_config = self.load_additional_config()
        print(self.additional_config)

    def load_additional_config(self) -> list[Any]:
        """
        Load an additional configuration file.
        :return:
        """
        configs = []
        # Load profile-specific configuration files
        profiles = get_nested_object(self.bootstrap_config, "application.config.profiles", None)
        if profiles:
            for profile in profiles.split(","):
                profile = profile.strip()
                if not profile:
                    continue
                for file_extension in [".yaml", ".json"]:
                    full_file_path = os.path.join(self.resource_directory, f"app-{profile}{file_extension}")
                    if not os.path.isfile(full_file_path):
                        continue
                    cfg = load_file(full_file_path, default_value={})
                    if cfg:
                        configs.append(cfg)

        # load static configuration file
        static_configs = get_nested_object(self.bootstrap_config, "application.config.static_configs", None)
        if static_configs:
            for static_config in static_configs.split(","):
                static_config = static_config.strip()
                if not static_config:
                    continue
                cfg = load_file(
                    os.path.join(self.resource_directory, static_config),
                    default_value={},
                )
                if cfg:
                    configs.append(cfg)

        logger.debug("Loaded %d additional configuration files.", len(configs))
        logger.info("Additional configuration loaded.")
        return configs
