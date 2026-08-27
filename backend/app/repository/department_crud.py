from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Department
from ..schemas.departments import DepartmentWrite
from .transaction import commit_or_rollback


def get_departments(db: Session) -> list[Department]:
    statement = select(Department).order_by(Department.id)
    return list(db.scalars(statement).all())


def get_department_by_id(db: Session, department_id: int) -> Department | None:
    return db.get(Department, department_id)


def create_department(db: Session, payload: DepartmentWrite) -> Department:
    record = Department(**payload.model_dump())
    db.add(record)
    commit_or_rollback(db)
    db.refresh(record)
    return record


def update_department(db: Session, record: Department, payload: DepartmentWrite) -> Department:
    record.department_name = payload.department_name
    commit_or_rollback(db)
    db.refresh(record)
    return record


def delete_department(db: Session, record: Department) -> None:
    db.delete(record)
    commit_or_rollback(db)
