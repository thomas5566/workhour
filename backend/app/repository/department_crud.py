from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Department


def get_departments(db: Session) -> list[Department]:
    statement = select(Department).order_by(Department.id)
    return list(db.scalars(statement).all())
