from sqlalchemy.orm import Session
# from sqlalchemy import text, func, cast, Numeric, union
# from .. import models
from ..models import User, Workhour, Department
from ..schemas import users


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
# def get_user(db: Session, username: str):
#     return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_department(db: Session, department_id: str):
    return db.query(User).filter(User.department_id == department_id).all()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_allusers_monthly(db: Session):
    join_query = db.query(User, Department, Workhour)\
        .join(Department, Department.id == User.department_id)\
        .join(Workhour, Workhour.user_id == User.id)

    for row in join_query.all():
        print("(")
        for item in row:
            print("   ", item)
        print(")")
    # return join_query
    # qry = (db.query(
    #     func.to_char(workhour.Workhour.date,
    #                     'YYYY-MM').label('year_month'),
    #     department.Department.department_name.label(
    #         'department_name'),
    #     user.User.username.label('user_name'),
    #     func.sum(workhour.Workhour.hour).label('total_hour'),
    #     func.sum(workhour.Workhour.overtime_hour).label(
    #         'total_overtime_hour'),
    #     func.sum(expen.Expenditure.price).label('total_pric')
    #     ).filter(user.User.id == workhour.Workhour.user_id and
    #              user.User.id == expen.Expenditure.user_id and
    #              user.User.department_id == department.Department.id ).group_by(
    #     'year_month',
    #     'department_name',
    #     'user_name'
    #     ).all())

    # print(qry)
    # return qry
    # qry1 = (db.query(
    #         func.to_char(workhour.Workhour.date,
    #                      'YYYY-MM').label('year_month'),
    #         # department.Department.department_name.label(
    #         #     'department_name'),
    #         # user.User.username.label('user_name'),
    #         func.sum(workhour.Workhour.hour).label('total_hour'),
    #         func.sum(workhour.Workhour.overtime_hour).label(
    #             'total_overtime_hour')
    #         # cast(expen.Expenditure.price, Numeric(10)).label('total_pric')
    #         ).group_by(
    #         func.to_char(workhour.Workhour.date,
    #                      'YYYY-MM').label('year_month'),
    #         # 'department_name',
    #         # 'user_name',
    #         # 'total_pric'
    #         ))

    # qry2 = (db.query(
    #         func.to_char(expen.Expenditure.date,
    #                      'YYYY-MM').label('year_month'),
    #         # department.Department.department_name.label(
    #         #     'department_name'),
    #         # user.User.username.label('user_name'),
    #         # cast(workhour.Workhour.hour, Numeric(10)).label('total_hour'),
    #         # cast(workhour.Workhour.overtime_hour, Numeric(
    #         #     10)).label('total_overtime_hour'),
    #         func.sum(expen.Expenditure.price).label('total_pric'),
    #         func.sum(expen.Expenditure.price).label('total_pric2')
    #         ).group_by(
    #         func.to_char(expen.Expenditure.date,
    #                      'YYYY-MM').label('year_month'),
    #         # 'department_name',
    #         # 'user_name',
    #         # 'total_hour',
    #         # 'total_overtime_hour'
    #         ))
    # all_queries = [qry1, qry2]
    # golden_set = union(*all_queries).alias()
    # result = db.query(golden_set).all()
    # print(result)
    # return result


def create_user(db: Session, user_item: users.UserCreate):
    db_user = User(
        username=user_item.username,
        # fullname=user.fullname,
        password=user_item.password,
        department_id=user_item.department_id,
        # is_active=True,
        # is_superuser=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
