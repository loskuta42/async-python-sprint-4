import logging.config
from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.schemas import short_url as short_url_schema
from src.services.urls_app import short_url_crud
from .tools import check_short_url
from src.core.logger import LOGGING

router = APIRouter()

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('api_logger')


@router.get(
    '/{url_id}',
    description='Redirect to original URL if it exists.'
)
async def get_origin_url(
        *,
        db: AsyncSession = Depends(get_session),
        url_id: str,
        request: Request
) -> Any:
    """
    Get short URL by ID.
    """
    short_url = await short_url_crud.get(db=db, url_id=url_id)
    check_short_url(short_url=short_url, url_id=url_id)
    result_object = await short_url_crud.add_request(
        db=db,
        obj=short_url,
        request=request
    )
    logger.info(
        'Redirect from %s to %s', short_url.short_url, short_url.origin_url
    )
    return RedirectResponse(result_object.origin_url)


@router.post(
    '/',
    response_model=short_url_schema.ShortUrlResponse,
    status_code=status.HTTP_201_CREATED,
    description='Create new short URL for original URL. Return short URL.'
)
async def create_short_url(
        *,
        db: AsyncSession = Depends(get_session),
        short_url_in: short_url_schema.ShortUrlCreate,
) -> Any:
    """
    Create new short URL.
    """
    short_url = await short_url_crud.create(db=db, obj_in=short_url_in)
    logger.info(
        'Create short_url %s for %s', short_url.short_url, short_url.origin_url
    )
    return short_url


@router.post(
    '/shorten',
    response_model=short_url_schema.MultiShortUrlResponse,
    status_code=status.HTTP_201_CREATED,
    description='Create a number of short URLs'
)
async def create_multi_short_urls(
        *,
        db: AsyncSession = Depends(get_session),
        short_urls_in: short_url_schema.MultiShortUrlCreate,
) -> Any:
    """
    Create new short URLs.
    """
    short_urls = await short_url_crud.create_multi(db=db, obj_in=short_urls_in)
    logger.info('Create a batch of short URLs')
    return short_urls


@router.delete(
    '/{url_id}',
    response_model=short_url_schema.ShortUrl,
    description=('Mark short URL as "deleted", in future '
                 'getting this short URl return 410 GONE')
)
async def delete_short_url(
        *,
        db: AsyncSession = Depends(get_session),
        url_id: str
) -> Any:
    """
    Delete a short URL.
    """
    short_url = await short_url_crud.get(db=db, url_id=url_id)
    check_short_url(short_url=short_url, url_id=url_id)
    short_url = await short_url_crud.delete(db=db, url_id=url_id)
    logger.info('Short URL with url_id - %s - mark as deleted', url_id)
    return short_url


@router.get(
    '/{url_id}/status',
    response_model=Union[
        short_url_schema.RequestCount,
        short_url_schema.ListRequest
    ],
    description=('Get status info of short URL. By default only'
                 ' requests number. Set "full-info" query '
                 'parameter for more info.')
)
async def get_short_url_status(
        *,
        full_info: Optional[bool] = Query(default=None, alias='full-info'),
        max_size: int = Query(
            default=10,
            ge=1,
            alias='max-size',
            description='Query max size.'
        ),
        offset: int = Query(
            default=0,
            ge=0,
            description='Query offset.'
        ),
        db: AsyncSession = Depends(get_session),
        url_id: str
) -> Any:
    """
    Get URL status.
    """
    short_url = await short_url_crud.get(db=db, url_id=url_id)
    check_short_url(short_url=short_url, url_id=url_id)
    result = await short_url_crud.get_status(
        db=db,
        url_id=short_url.id,
        full_info=full_info,
        limit=max_size,
        offset=offset
    )
    if isinstance(result, int):
        logger.info('Send short version of status for url_id - %s', url_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'requests_number': result})
    logger.info('Send fill version of status for url_id - %s', url_id)
    return result
