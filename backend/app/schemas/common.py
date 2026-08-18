from .base import BaseModel


class MessageResponse(BaseModel):
    """Stable response envelope for operations that return only a message."""

    detail: str


class ErrorResponse(BaseModel):
    """Sanitized API error envelope that never exposes internal exceptions."""

    detail: str
