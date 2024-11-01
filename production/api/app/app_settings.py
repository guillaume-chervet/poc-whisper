import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable


@dataclass(kw_only=True)
class AppSettings:
    redis_host: str
    redis_port: int
    url_slimfaas: str
    server_host: str
    server_port: int
    oidc_issuer: Optional[str] = None
    oidc_authority: Optional[str] = "true"


class Settings:
    def __init__(self):
        self.app_settings = {}

    def overload(self, func: Callable):
        self.app_settings = func(self.app_settings)
        return self

    def build(self):
        return self.app_settings


def init_settings_file(settings_dir: str, app_environment: str = "development") -> dict:
    base_path = Path(settings_dir)

    # Load settings from default file
    try:
        settings_path = base_path / 'settings.json'
        print("settings_path: ", settings_path)
        with open(settings_path, 'r') as data:
            settings_json = json.load(data)
    except FileNotFoundError:
        logging.warning(f"Default Settings file not found in {settings_dir}")
        settings_json = {}

    # Load settings from environment specific file
    try:
        settings_path = base_path / ('settings.' + app_environment + '.json')
        with open(settings_path, 'r') as data:
            settings_json.update(json.load(data))
    except FileNotFoundError:
        logging.warning(f"Settings file for environment {app_environment} not found in {settings_dir}")

    return settings_json


def init_settings_environments(settings: dict) -> dict:
    for key, value in settings.items():
        if os.environ.get(key, None) is not None:
            settings[key.lower()] = os.environ.get(key)
    return settings


app_settings_instance = None
def app_settings_factory_get():
    global app_settings_instance
    if app_settings_instance is not None:
        return app_settings_instance

    setting_directory = os.path.join(os.path.dirname(__file__))
    python_environment = os.environ.get("PYTHON_ENVIRONMENT", "development")
    app_settings = AppSettings(**(Settings()
            .overload(lambda app_settings : init_settings_file(setting_directory, python_environment))
            .overload(init_settings_environments)
            .build()))
    app_settings_instance = app_settings
    return app_settings