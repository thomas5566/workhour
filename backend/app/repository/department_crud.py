from sqlalchemy.orm import Session

# from .. import models
from ..models import Department


def get_departments(db: Session):
    return db.query(Department).all()
