import logging.config
from fastapi import HTTPException, status

from src.models.urls_app import ShortUrl
from src.core.logger import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def check_short_url(short_url: ShortUrl, url_id: str):
    if not short_url:
        logger.error('Raise 404 for url_id %s', url_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item not found'
        )
    elif short_url.deleted:
        logger.error('URL with url_id -  %s - was deleted', url_id)
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item is deleted'
        )
