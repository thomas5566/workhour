from typing import Annotated

from fastapi import Depends, Path, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db

# Annotated aliases keep FastAPI's injection metadata next to the Python type,
# so route signatures remain type-safe without Depends calls as defaults.
DatabaseSession = Annotated[Session, Depends(get_db)]
LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]

# Bound collection queries before they reach SQLAlchemy. The generous upper
# limit preserves current clients while preventing accidental unbounded reads.
PageOffset = Annotated[int, Query(ge=0)]
PageLimit = Annotated[int, Query(ge=1, le=1000)]

# Database identifiers start at one. Shared aliases keep invalid IDs from
# reaching repositories while preserving whether FastAPI reads a path or query.
PositivePathId = Annotated[int, Path(gt=0)]
PositiveQueryId = Annotated[int, Query(gt=0)]
