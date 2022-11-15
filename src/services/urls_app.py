from src.models.urls_app import Request as RequestModel
from src.models.urls_app import ShortUrl as ShortUrlModel
from src.schemas.short_url import MultiShortUrlCreate, ShortUrlCreate

from .base import RepositoryShotUrlDB


class RepositoryShortUrl(
    RepositoryShotUrlDB[
        ShortUrlModel,
        RequestModel,
        ShortUrlCreate,
        MultiShortUrlCreate
    ]
):
    pass


short_url_crud = RepositoryShortUrl(ShortUrlModel, RequestModel)
