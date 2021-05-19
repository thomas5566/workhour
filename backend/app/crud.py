from sqlalchemy.orm import Session
from app import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
            username=user.username,
            fullname=user.fullname, 
            password=user.password
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
''''''

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
''''''

def get_workhour(db: Session, workhour_id: int):
    return db.query(models.Workhour).filter(models.Workhour.id == workhour_id).first()

def get_workhours(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Workhour).offset(skip).limit(limit).all()

def get_workhours_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Workhour).filter(models.Workhour.user_id == user_id).offset(skip).limit(limit).all()

def get_workhours_by_task_id(db: Session, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Workhour).filter(models.Workhour.task_id == task_id).offset(skip).limit(limit).all()

def get_workhours_by_user_task(db: Session, user_id: int, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Workhour).filter(models.Workhour.user_id == user_id, models.Workhour.task_id == task_id).offset(skip).limit(limit).all()

def create_workhour(db: Session, workhour: schemas.WorkhourCreate):
    db_workhour = models.Workhour(
    	user_id=workhour.user_id, 
    	task_id=workhour.task_id, 
    	date=workhour.date, 
    	hour=workhour.hour, 
    	description=workhour.description,
        is_overtime=workhour.is_overtime)
    db.add(db_workhour)
    db.commit()
    db.refresh(db_workhour)
    return db_workhour

def update_workhour(db: Session, workhour_id: int, workhour: schemas.WorkhourUpdate):
    db_workhour = db.query(models.Workhour).filter(models.Workhour.id == workhour_id).first()
    if db_workhour is None:
        return None
    for var, value in vars(workhour).items():
        setattr(db_workhour, var, value) if value else None
    db.add(db_workhour)
    db.commit()
    db.refresh(db_workhour)
    return db_workhour