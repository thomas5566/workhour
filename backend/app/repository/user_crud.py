from sqlalchemy.orm import Session
from sqlalchemy import text

from .. import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
# def get_user(db: Session, username: str):
#     return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_department(db: Session, department_id: str):
    return db.query(models.User).filter(models.User.department_id == department_id).all()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        # fullname=user.fullname,
        password=user.password,
        department_id=user.department_id,
        # is_active=True,
        # is_superuser=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user