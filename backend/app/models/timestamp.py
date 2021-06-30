from sqlalchemy import Column, Integer, Date
from sqlalchemy.sql import func


class IdMixin(object):
    id = Column(Integer, primary_key=True, index=True)


class TimestampMixin(object):
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())
