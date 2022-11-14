from fastapi import APIRouter

from src.api.v1.short_url import router


api_router = APIRouter()

api_router.include_router(router, prefix="/short_url", tags=["short_url"])
