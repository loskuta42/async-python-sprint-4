from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from src.db.db import Base


class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('short_urls.id'))
    made_at = Column(DateTime, index=True, default=datetime.utcnow)
    client_host = Column(String, nullable=False)
    client_port = Column(Integer, nullable=False)


class ShortUrl(Base):
    __tablename__ = "short_urls"
    id = Column(Integer, primary_key=True)
    origin_url = Column(URLType, nullable=False)
    short_url = Column(URLType,  nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    requests = relationship('Request', backref='url', cascade="all, delete")
    short_form = Column(String(6), nullable=False)
    deleted = Column(Boolean, default=False)
