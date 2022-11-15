import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn, Field

from .logger import LOGGING


logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    app_title: str = 'ShortUrlApp'
    database_dsn: PostgresDsn
    project_name: str = Field('ShortUrl', env='PROJECT_NAME')
    project_host: str = Field('127.0.0.1', env='PROJECT_HOST')
    project_port: int = Field(8080, env='PROJECT_PORT')
    base_dir: str = Field(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), env='BASE_DIR')

    class Config:
        env_file = '.env'


app_settings = AppSettings()
