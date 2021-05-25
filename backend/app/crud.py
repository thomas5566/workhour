# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from sqlalchemy.sql import func
# from . import models, schemas

# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()

# def get_user_by_username(db: Session, username: str):
#     return db.query(models.User).filter(models.User.username == username).first()

# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()

# def create_user(db: Session, user: schemas.UserCreate):
#     db_user = models.User(
#             username=user.username,
#             fullname=user.fullname, 
#             password=user.password
#         )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# def get_task(db: Session, task_id: int):
#     return db.query(models.Task).filter(models.Task.id == task_id).first()

# def get_task_by_taskname(db: Session, taskname: str):
#     return db.query(models.Task).filter(models.Task.taskname == taskname).first()

# def get_tasks(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Task).offset(skip).limit(limit).all()

# def create_task(db: Session, task: schemas.TaskCreate):
#     db_task = models.Task(
#     	taskname=task.taskname, 
#     	fullname=task.fullname, 
#     	organization=task.organization)
#     db.add(db_task)
#     db.commit()
#     db.refresh(db_task)
#     return db_task

# def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
#     db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
#     if db_task is None:
#         return None
#     for var, value in vars(task).items():
#         setattr(db_task, var, value) if value else None
#     db.add(db_task)
#     db.commit()
#     db.refresh(db_task)
#     return db_task

# def get_expentask(db: Session, expentask_id: int):
#     return db.query(models.ExpenTask).filter(models.ExpenTask.id == expentask_id).first()

# def get_expentask_by_expentaskname(db: Session, expentaskname: str):
#     return db.query(models.ExpenTask).filter(models.ExpenTask.expentask_name == expentaskname).first()

# def get_expentasks(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.ExpenTask).offset(skip).limit(limit).all()

# def create_expentask(db: Session, expentask: schemas.ExpenTaskCreate):
#     db_expentask = models.ExpenTask(
#     	expentaskname=expentask.expentask_name)
#     db.add(db_expentask)
#     db.commit()
#     db.refresh(db_expentask)
#     return db_expentask

# def update_expentask(db: Session, expentask_id: int, expentask: schemas.ExpenTaskUpdate):
#     db_expentask = db.query(models.ExpenTask).filter(models.ExpenTask.id == expentask_id).first()
#     if db_expentask is None:
#         return None
#     for var, value in vars(db_expentask).items():
#         setattr(db_expentask, var, value) if value else None
#     db.add(db_expentask)
#     db.commit()
#     db.refresh(db_expentask)
#     return db_expentask

# def get_workhour(db: Session, workhour_id: int):
#     return db.query(models.Workhour).filter(models.Workhour.id == workhour_id).first()

# def get_workhours(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Workhour).order_by(text("date desc")).offset(skip).limit(limit).all()

# def get_workhours_by_user_id(db: Session, user_id, skip: int = 0, limit: int = 100):
#     return db.query(models.Workhour).filter(models.Workhour.user_id == user_id).offset(skip).limit(limit).all()

# # def get_totalworkhours_by_user_id(db: Session, skip: int = 0):
# #     return db.query(func.sum(models.Workhour.hour)).offset(skip).first()

# def get_workhours_by_task_id(db: Session, task_id: int, skip: int = 0, limit: int = 100):
#     return db.query(models.Workhour).filter(models.Workhour.task_id == task_id).offset(skip).limit(limit).all()

# def get_workhours_by_user_task(db: Session, user_id: int, task_id: int, skip: int = 0, limit: int = 100):
#     return db.query(models.Workhour).filter(models.Workhour.user_id == user_id, models.Workhour.task_id == task_id).offset(skip).limit(limit).all()

# def create_workhour(db: Session, workhour: schemas.WorkhourCreate):
#     db_workhour = models.Workhour(
#     	user_id=workhour.user_id, 
#     	task_id=workhour.task_id, 
#     	date=workhour.date,
#     	hour=workhour.hour, 
#     	description=workhour.description,
#         is_overtime=workhour.is_overtime)
#     db.add(db_workhour)
#     db.commit()
#     db.refresh(db_workhour)
#     return db_workhour

# def update_workhour(db: Session, workhour_id: int, workhour: schemas.WorkhourUpdate):
#     db_workhour = db.query(models.Workhour).filter(models.Workhour.id == workhour_id).first()
#     if db_workhour is None:
#         return None
#     for var, value in vars(workhour).items():
#         setattr(db_workhour, var, value) if value else None
#     db.add(db_workhour)
#     db.commit()
#     db.refresh(db_workhour)
#     return db_workhour

# def get_expen(db: Session, expen_id: int):
#     return db.query(models.Expenditure).filter(models.Expenditure.id == expen_id).first()

# def get_expens(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Expenditure).order_by(text("date desc")).offset(skip).limit(limit).all()

# def get_expens_by_user_expentask(db: Session, user_id: int, expentask_id: int, skip: int = 0, limit: int = 100):
#     return db.query(models.Expenditure).filter(models.Expenditure.user_id == user_id, models.Expenditure.expentask_id == expentask_id).offset(skip).limit(limit).all()

# def get_expens_by_user_id(db: Session, user_id, skip: int = 0, limit: int = 100):
#     return db.query(models.Expenditure).filter(models.Expenditure.user_id == user_id).offset(skip).limit(limit).all()

# def get_expens_by_expentask_id(db: Session, expentask_id: int, skip: int = 0, limit: int = 100):
#     return db.query(models.Expenditure).filter(models.Expenditure.expentask_id == expentask_id).offset(skip).limit(limit).all()

# def create_expen(db: Session, expen: schemas.ExpenditureCreate):
#     db_expen = models.Expenditure(
#             user_id=expen.user_id,
#     	    expentask_id=expen.expentask_id,
#             date=expen.date,
#             price=expen.price,
#             description=expen.description,
#         )
#     db.add(db_expen)
#     db.commit()
#     db.refresh(db_expen)
#     return db_expen

# def update_expen(db: Session, expen_id: int, expen: schemas.ExpenditureUpdate):
#     db_expen = db.query(models.Expenditure).filter(models.Expenditure.id == expen_id).first()
#     if db_expen is None:
#         return None
#     for var, value in vars(expen).items():
#         setattr(db_expen, var, value) if value else None
#     db.add(db_expen)
#     db.commit()
#     db.refresh(db_expen)
#     return db_expen

# def delete_expen(db: Session, user_id: int, expen_id: int):
#     db.query(models.Expenditure).filter(
#                                 models.Expenditure.user_id == user_id,
#                                 models.Expenditure.id == expen_id).delete(synchronize_session=False)
    
#     db.commit()
#     return "Expen hase being delete"
