from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def commit_or_rollback(db: Session) -> None:
    """Commit one repository operation and restore the session on failure."""
    try:
        db.commit()
    except SQLAlchemyError:
        # A failed flush/commit leaves SQLAlchemy sessions unusable until rollback.
        db.rollback()
        raise
