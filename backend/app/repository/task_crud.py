from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.sql.expression import true
# from .. import models, schemas

from ..models import task
from ..schemas import tasks

def get_task(db: Session, task_id: int):
    return db.query(task.Task).filter(task.Task.id == task_id).first()


def get_task_by_taskname(db: Session, taskname: str):
    return db.query(task.Task).filter(task.Task.taskname == taskname).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(task.Task).filter(task.Task.is_active == "true").offset(skip).limit(limit).all()


def create_task(db: Session, task_items: tasks.TaskCreate):
    db_task = task.Task(
        taskname=task_items.taskname,
        fullname=task_items.fullname,
        organization=task_items.organization)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_items: tasks.TaskUpdate):
    db_task = db.query(task.Task).filter(task.Task.id == task_id).first()
    if db_task is None:
        return None
    for var, value in vars(task).items():
        setattr(db_task, var, value) if value else None
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(id: int, db: Session):
    task_item = db.query(task.Task).filter(
        task.Task.id == id)

    if not task_item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")

    task_item.delete(synchronize_session=False)
    db.commit()
    return "Task hase being delete"