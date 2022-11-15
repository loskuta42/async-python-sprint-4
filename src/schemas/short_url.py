from datetime import datetime
from typing import List, Union

from pydantic import BaseModel


class Request(BaseModel):
    made_at: datetime
    client_host: str
    client_port: int

    class Config:
        orm_mode = True


class ListRequest(BaseModel):
    __root__: List[Request]


class RequestCount(BaseModel):
    description: Union[str, None] = None
    requests_number: int


class ShortUrlBase(BaseModel):
    origin_url: str


class ShortUrlResponse(BaseModel):
    description: Union[str, None] = None
    short_url: str

    class Config:
        orm_mode = True


class OneShortUrlInfo(BaseModel):
    short_form: str
    short_url: str

    class Config:
        orm_mode = True


class MultiShortUrlResponse(BaseModel):
    __root__: List[OneShortUrlInfo]


class ShortUrlCreate(ShortUrlBase):
    pass


class MultiShortUrlCreate(BaseModel):
    __root__: List[ShortUrlBase]


class ShortUrl(ShortUrlBase):
    description: Union[str, None] = None
    id: int
    origin_url: str
    short_url: str
    created_at: datetime
    short_form: str
    deleted: bool

    class Config:
        orm_mode = True


class ShortUrlInDB(ShortUrlBase):
    id: int
    origin_url: str
    short_url: str
    created_at: datetime
    requests: list[Request] = []
    short_form: str
    deleted: bool

    class Config:
        orm_mode = True
