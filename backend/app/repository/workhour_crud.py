from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi import HTTPException, status
# from .. import models, schemas

from ..models import workhour
from ..schemas import whorkhours


def get_workhour(db: Session, workhour_id: int):
    return db.query(workhour.Workhour).order_by(text("date desc")).filter(
        workhour.Workhour.id == workhour_id).first()


# def get_workhours(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Workhour).order_by(text("date desc")).offset(skip).limit(limit).all()
def get_workhours(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(workhour.Workhour).order_by(text("date desc")).filter(
        workhour.Workhour.user_id == user_id).offset(skip).limit(limit).all()


# def get_worklist_by_group(db: Session, group: str):
#     if group == ''
#     groupWorklist = db.query(models.Workhour).all()

def get_workhours_by_user_id(db: Session, user_id, skip: int = 0, limit: int = 100):
    return db.query(workhour.Workhour).order_by(text("date desc")).filter(
        workhour.Workhour.user_id == user_id).offset(skip).limit(limit).all()


def get_monthlyworkhours_by_user_id(db: Session, user_id):
    qry = (db.query(
        # models.Workhour,
        # models.Workhour.id,
        # models.Workhour.task_id,
        # models.Workhour.date,
        # models.Workhour.hour,
        # models.Workhour.overtime_hour,
        # #strftime* for year-month works on sqlite;
        # @todo: find proper function for mysql (as in the question)
        # Also it is not clear if only MONTH part is enough, so that
        # May-2001 and May-2009 can be joined, or YEAR-MONTH must be used
        func.to_char(workhour.Workhour.date,
                     'YYYY-MM').label('year_month'),
        func.sum(workhour.Workhour.hour).label('total_hour'),
        func.sum(workhour.Workhour.overtime_hour).label(
            'total_overtime_hour')
    )
        .order_by(text("year_month desc"))
        # optionally check only last 2 month data (could have partial months)
        .filter(workhour.Workhour.user_id == user_id)
        .group_by(
        func.to_char(workhour.Workhour.date, 'YYYY-MM').label('year_month'),
        # models.Workhour.id,
        # models.Workhour.task_id,
        # models.Workhour.date,
        # models.Workhour.hour,
        # models.Workhour.overtime_hour,
        # func.month(models.Workhour.date),
        # func.date_trunc('month', models.Workhour.date),
    )
        .all()
        # comment this line out to see all the groups
        # .having(func.count()>1)
    )
    # print(qry)
    return qry


def get_workhours_by_task_id(db: Session, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(workhour.Workhour).order_by(text("date desc")).filter(
        workhour.Workhour.task_id == task_id).offset(skip).limit(limit).all()


def get_workhours_by_user_task(db: Session, user_id: int, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(workhour.Workhour).order_by(text("date desc")).filter(
        workhour.Workhour.user_id == user_id, workhour.Workhour.task_id == task_id).offset(
            skip).limit(limit).all()


def create_workhour(db: Session, workhour_items: whorkhours.WorkhourCreate):
    db_workhour = workhour.Workhour(
        user_id=workhour_items.user_id,
        task_id=workhour_items.task_id,
        date=workhour_items.date,
        hour=workhour_items.hour,
        description=workhour_items.description,
        is_overtime=workhour_items.is_overtime,
        overtime_hour=workhour_items.overtime_hour
    )
    db.add(db_workhour)
    db.commit()
    db.refresh(db_workhour)
    return db_workhour


def update_workhour(workhour_id: int, workhour_items: whorkhours.WorkhourUpdate, db: Session,  user_id: int):
    db_workhour = db.query(workhour.Workhour).filter(
        workhour.Workhour.id == workhour_id)

    if not db_workhour.first():
        return 0
    workhour_items.__dict__.update(user_id=user_id)
    db_workhour.update(workhour_items.__dict__)
    db.commit()
    return 1
    # if db_workhour is None:
    #     return None
    # for var, value in vars(workhour).items():
    #     setattr(db_workhour, var, value) if value else None
    # db.add(db_workhour)
    # db.commit()
    # db.refresh(db_workhour)
    # return db_workhour


def delete_workhour(id: int, db: Session):
    workhour_items = db.query(workhour.Workhour).filter(
        workhour.Workhour.id == id)

    if not workhour_items.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")

    workhour_items.delete(synchronize_session=False)
    db.commit()
    return "Workhour hase being delete"
