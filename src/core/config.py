import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

from .logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'urler')
PROJECT_HOST = os.getenv('PROJECT_HOST', '127.0.0.1')
PROJECT_PORT = os.getenv('PROJECT_PORT', 8080)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):
    app_title: str = "UrlsApp"
    database_dsn: PostgresDsn

    class Config:
        env_file = '.env'


app_settings = AppSettings()
