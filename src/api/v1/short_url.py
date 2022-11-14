from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.models.urls_app import Request as RequestModel
from src.schemas import short_url as short_url_schema
from src.services.urls_app import short_url_crud


router = APIRouter()


@router.get('/{url_id}')
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
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )
    elif short_url.deleted:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item is deleted'
        )
    result_object = await short_url_crud.add_request(db=db, obj=short_url, request=request)
    return RedirectResponse(result_object.origin_url)


@router.post(
    '/', response_model=short_url_schema.ShortUrlResponse, status_code=status.HTTP_201_CREATED
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
    return short_url


@router.post(
    '/shorten',
    response_model=short_url_schema.MultiShortUrlResponse,
    status_code=status.HTTP_201_CREATED
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
    return short_urls


@router.delete("/{url_id}", response_model=short_url_schema.ShortUrl)
async def delete_short_url(*, db: AsyncSession = Depends(get_session), url_id: str) -> Any:
    """
    Delete an entity.
    """
    short_url = await short_url_crud.get(db=db, url_id=url_id)
    if not short_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='URL not found')
    short_url = await short_url_crud.delete(db=db, url_id=url_id)
    return short_url


@router.get('/{url_id}/status', response_model=Union[short_url_schema.RequestCount, short_url_schema.ListRequest])
async def get_short_url_status(
        *,
        full_info: Optional[bool] = Query(default=None, alias="full-info"),
        max_size: int = Query(default=10, alias='max-size'),
        offset: int = 0,
        db: AsyncSession = Depends(get_session),
        url_id: str
) -> Any:
    """
    Get URL status.
    """
    short_url = await short_url_crud.get(db=db, url_id=url_id)
    if not short_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='URL not found')
    elif short_url.deleted:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item is deleted')
    result = await short_url_crud.get_status(
        db=db,
        url_id=short_url.id,
        full_info=full_info,
        limit=max_size,
        offset=offset
    )
    if isinstance(result, int):
        return JSONResponse(status_code=200, content={'requests_number': result})
    return result
