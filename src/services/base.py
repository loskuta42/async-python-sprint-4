from typing import Any, Generic, Optional, Type, TypeVar, Union

import shortuuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request as ClientRequest
from sqlalchemy.future import select

from src.core.config import app_settings
from src.db.db import Base


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_status(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def add_request(self, *args, **kwargs):
        raise NotImplementedError

    def create_multi(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)
RequestTypeModel = TypeVar("RequestTypeModel", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
MultiCreateSchemaType = TypeVar("MultiCreateSchemaType", bound=BaseModel)


class RepositoryShotUrlDB(
    Repository,
    Generic[
        ModelType,
        RequestTypeModel,
        CreateSchemaType,
        MultiCreateSchemaType
    ]
):
    def __init__(
            self,
            model: Type[ModelType],
            request: Type[ModelType]
    ):
        self._model = model
        self._request_model = request

    async def get(
            self,
            db: AsyncSession,
            url_id: Any
    ) -> Optional[ModelType]:
        statement = select(
            self._model
        ).where(
            self._model.short_form == url_id
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_status(
            self,
            db: AsyncSession,
            url_id: Any,
            limit: int,
            offset: int,
            full_info: Optional[bool],
    ) -> Union[int, list[ModelType]]:
        if not full_info:
            statement = select(
                self._request_model
            ).where(
                self._request_model.url_id == url_id
            )
            results = await db.execute(statement=statement)
            requests_number = len(results.fetchall())
            return requests_number
        statement = select(
            self._request_model
        ).where(
            self._request_model.url_id == url_id
        ).offset(offset).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    def create_obj(self, obj_in_data):
        extra_obj_info = {}
        short_form = shortuuid.ShortUUID().random(length=6)
        extra_obj_info['short_form'] = short_form
        short_url = ''.join(
            [
                'http://',
                app_settings.project_host,
                ':',
                str(app_settings.project_port),
                '/api/v1/short_url/',
                short_form
            ])
        extra_obj_info['short_url'] = short_url
        obj_in_data.update(extra_obj_info)
        return self._model(**obj_in_data)

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.create_obj(obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_multi(
            self,
            db: AsyncSession,
            *,
            obj_in: MultiCreateSchemaType
    ) -> ModelType:
        objs_in_data = jsonable_encoder(obj_in)
        objects_to_db = [
            self.create_obj(obj_in_data)
            for obj_in_data in objs_in_data
        ]
        db.add_all(objects_to_db)
        await db.commit()
        for obj in objects_to_db:
            await db.refresh(obj)
        return objects_to_db

    async def add_request(
            self,
            db: AsyncSession,
            *,
            obj: ModelType,
            request: ClientRequest
    ) -> ModelType:
        request_obj = self._request_model(
            url=obj,
            client_host=request.client.host,
            client_port=request.client.port
        )
        db.add(request_obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(
            self,
            db: AsyncSession,
            *,
            url_id: str
    ) -> ModelType:
        db_obj = await self.get(db, url_id)
        db_obj.deleted = True
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
