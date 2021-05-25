from sqlalchemy.orm import Session
from .. import models, schemas

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_task_by_taskname(db: Session, taskname: str):
    return db.query(models.Task).filter(models.Task.taskname == taskname).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        taskname=task.taskname,
        fullname=task.fullname,
        organization=task.organization)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        return None
    for var, value in vars(task).items():
        setattr(db_task, var, value) if value else None
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
