from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi import HTTPException, status
# from .. import models, schemas

from ..models import Workhour, User, CstShop
from ..schemas import whorkhours


def get_workhour(db: Session, workhour_id: int):
    return db.query(Workhour).order_by(text("start_date desc")).filter(
        Workhour.id == workhour_id, Workhour.active == True).first()


# def get_workhours(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Workhour).order_by(text("date desc")).offset(skip).limit(limit).all()
def get_workhours(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Workhour).order_by(text("start_date desc")).filter(
        Workhour.user_id == user_id, Workhour.active == True).offset(skip).limit(limit).all()

def get_all_workhours(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(Workhour).order_by(text("start_date desc")).filter(Workhour.active == True).offset(skip).limit(limit).all()


def get_worklist_by_yearmonth(db: Session):
    year_month = func.date_trunc('month', Workhour.start_date).label('year_month')
    qry = db.query(year_month, func.count(Workhour.id).label('total_events')).filter(
                Workhour.active == True).group_by(year_month).order_by(text("year_month asc")).all()
    return qry


def get_worklist_by_userid(db: Session):
    qry = db.query(Workhour.user_id, func.count(Workhour.id).label('total_events'), User.username, User.fullname).join(
        User, Workhour.user_id == User.id).filter(
        Workhour.active == True).group_by(
        Workhour.user_id, User.username, User.fullname).all()
    
    return qry


def get_worklist_by_shopid(db: Session):
    qry = db.query(Workhour.shop_id, func.count(Workhour.id).label('total_events'), CstShop.shop_name).join(
                    CstShop, CstShop.id == Workhour.shop_id
                    ).filter(
                    Workhour.active == True).group_by(
                    Workhour.shop_id, CstShop.shop_name).all()
    return qry


def get_workhours_by_user_id(db: Session, user_id, skip: int = 0, limit: int = 100):
    return db.query(Workhour).order_by(text("start_date desc")).filter(
        Workhour.user_id == user_id, Workhour.active == True).offset(skip).limit(limit).all()


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
        func.to_char(Workhour.start_date,
                     'YYYY-MM').label('year_month'),
        func.sum(Workhour.hour).label('total_hour'),
        func.sum(Workhour.overtime_hour).label(
            'total_overtime_hour')
    )
        .order_by(text("year_month desc"))
        # optionally check only last 2 month data (could have partial months)
        .filter(Workhour.user_id == user_id)
        .group_by(
        func.to_char(Workhour.date, 'YYYY-MM').label('year_month'),
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
    return db.query(Workhour).order_by(text("start_date desc")).filter(
        Workhour.task_id == task_id).offset(skip).limit(limit).all()


def get_workhours_by_user_task(db: Session, user_id: int, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(Workhour).order_by(text("start_date desc")).filter(
        Workhour.user_id == user_id, Workhour.task_id == task_id).offset(
            skip).limit(limit).all()


def create_workhour(db: Session, workhour_items: whorkhours.WorkhourCreate):
    db_workhour = Workhour(
        user_id=workhour_items.user_id,
        task_id=workhour_items.task_id,
        shop_id=workhour_items.shop_id,
        start_date=workhour_items.start_date,
        hour=workhour_items.hour,
        description=workhour_items.description,
        case_close=workhour_items.case_close,
        overtime_hour=workhour_items.overtime_hour,
        end_date=workhour_items.end_date,
        todo=workhour_items.todo,
        cause_issue=workhour_items.cause_issue,
        processing_method=workhour_items.processing_method
    )
    db.add(db_workhour)
    db.commit()
    db.refresh(db_workhour)
    return db_workhour


def update_workhour(workhour_id: int, workhour_items: whorkhours.WorkhourUpdate, db: Session,  user_id: int):
    db_workhour = db.query(Workhour).filter(
        Workhour.id == workhour_id)

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
    workhour_items = db.query(Workhour).filter(
        Workhour.id == id)

    if not workhour_items.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")

    workhour_items.delete(synchronize_session=False)
    db.commit()
    return "Workhour hase being delete"
