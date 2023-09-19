from sqlalchemy.orm import Session, contains_eager
# from sqlalchemy import text
from fastapi import HTTPException, status
# from .. import models, schemas

from ..models import Task, Workhour, User, CstShop
from ..schemas import tasks


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def get_task_by_taskname(db: Session, taskname: str):
    return db.query(Task).filter(Task.taskname == taskname).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.is_active == "true").offset(skip).limit(limit).all()
    # results = db.query(task.Task, workhour.Workhour).join(workhour.Workhour).all()
    # return results    


def get_tasks_by_worklist(db: Session):
    # query = (db.query(task.Task.id.label('task_id'),
    #                   task.Task.taskname.label('task_name'),
    #                   user.User.username.label('user_name'),
    #                   workhour.Workhour.user_id.label('user_id'),
    #                   workhour.Workhour.task_id.label('worklist_task_id'),
    #                   workhour.Workhour.date.label('worklist_date'),
    # 	              workhour.Workhour.hour.label('worklist_hour'),
    #                   workhour.Workhour.is_overtime.label('worklist_overtime'),
    # 	              workhour.Workhour.overtime_hour.label('worklist_overtime_hour'),
    #                   workhour.Workhour.description.label('worklist_description'),
    #                   )
    #         .join(workhour.Workhour)
    #         .join(user.User)
    #         .filter(task.Task.id == workhour.Workhour.task_id)
    #         .filter(user.User.id == workhour.Workhour.user_id)
    #         .order_by(text('worklist_date desc'))
    #         ).all()
    # print(query)
    # return query

    q = (db.query(Task)
         .join(Workhour)
         .join(User)
         # @note: here we are tricking sqlalchemy to think that we loaded all these relationships,
         # even though we filter them out by version. Please use this only to get data and display,
         # but not to continue working with it as if it were a regular UnitOfWork
         .options(
        contains_eager(Task.workhours).
        contains_eager(Workhour.task)
        # contains_eager(user.User.department)
    )
        .filter(Task.id == Workhour.task_id)
        .order_by(Workhour.date.desc())
    ).all()

    return q


def create_task(db: Session, task_items: tasks.TaskCreate):
    db_task = Task(
        taskname=task_items.taskname,
        fullname=task_items.fullname,
        organization=task_items.organization)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_items: tasks.TaskUpdate):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        return None
    for var, value in vars(task_items).items():
        setattr(db_task, var, value) if value else None
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(id: int, db: Session):
    task_item = db.query(Task).filter(
        Task.id == id)

    if not task_item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")

    task_item.delete(synchronize_session=False)
    db.commit()
    return "Task hase being delete"
