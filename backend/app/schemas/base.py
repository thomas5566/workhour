from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    """Shared schema base with SQLAlchemy object serialization enabled."""

    model_config = ConfigDict(from_attributes=True)
