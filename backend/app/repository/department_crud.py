from sqlalchemy.orm import Session

# from .. import models
from ..models import department

def get_departments(db: Session):
    return db.query(department.Department).all()