from collections.abc import Callable
from datetime import date

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.database import Base
from app.models import (
    CstShop,
    Department,
    Expenditure,
    ExpenTask,
    Task,
    User,
    Workhour,
)
from app.repository import (
    expen_crud,
    expentask_crud,
    task_crud,
    user_crud,
    workhour_crud,
)
from app.schemas.allfull import (
    ExpenditureFull,
    ExpenTaskFull,
    TaskFull,
    UserFull,
    WorkhourFull,
)
from app.schemas.expens import ExpenditureCreate, ExpenditureUpdate
from app.schemas.expentasks import ExpenTaskCreate, ExpenTaskUpdate
from app.schemas.tasks import TaskCreate, TaskGYBase, TaskUpdate
from app.schemas.users import DataTotal
from app.schemas.workhours import WorkhourCreate, WorkhourUpdate


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_task_repository_crud_uses_sqlalchemy_two_api(db: Session) -> None:
    created = task_crud.create_task(
        db,
        TaskCreate(
            taskname="modernization",
            fullname="Backend modernization",
            organization="WorkHour",
        ),
    )

    assert task_crud.get_task(db, created.id) is created
    assert task_crud.get_tasks(db) == [created]

    updated = task_crud.update_task(
        db,
        created.id,
        TaskUpdate(
            taskname="modernization-phase-1",
            fullname="Backend modernization phase 1",
            organization="WorkHour",
        ),
    )
    assert updated is not None
    assert updated.taskname == "modernization-phase-1"

    assert task_crud.delete_task(created.id, db) is True
    assert task_crud.get_task(db, created.id) is None


def test_workhour_repository_crud_preserves_owner(db: Session) -> None:
    created = workhour_crud.create_workhour(
        db,
        WorkhourCreate(
            task_id=1,
            shop_id=1,
            start_date=date(2026, 8, 17),
            end_date=date(2026, 8, 17),
            hour=8,
            overtime_hour=0,
            case_close=False,
        ),
        user_id=12,
    )

    assert workhour_crud.get_workhours(db, user_id=12) == [created]

    updated = workhour_crud.update_workhour(
        created.id,
        WorkhourUpdate(
            task_id=1,
            shop_id=1,
            start_date=date(2026, 8, 17),
            end_date=date(2026, 8, 17),
            hour=7.5,
            overtime_hour=0.5,
            case_close=True,
        ),
        db,
        user_id=12,
    )
    assert updated is not None
    assert updated.user_id == 12
    assert float(updated.hour) == 7.5

    assert workhour_crud.delete_workhour(created.id, db) is True
    assert workhour_crud.get_workhour(db, created.id) is None


def test_workhour_response_graph_avoids_n_plus_one_queries(db: Session) -> None:
    department = Department(department_name="IT")
    user = User(
        username="query-user",
        fullname="Query User",
        password="hash",
        department=department,
    )
    task = Task(
        taskname="query-task",
        fullname="Query Task",
        organization="WorkHour",
    )
    shop = CstShop(
        shop_name="Taipei shop",
        shop_number="TPE-01",
        task=task,
    )
    db.add_all(
        [
            Workhour(
                user=user,
                task=task,
                shop=shop,
                start_date=date(2026, 8, 17 + index),
                end_date=date(2026, 8, 17 + index),
                hour=8,
                overtime_hour=0,
                case_close=False,
                active=True,
            )
            for index in range(3)
        ]
    )
    db.commit()
    db.expire_all()

    statements: list[str] = []

    def count_statement(*args) -> None:
        statements.append(args[2])

    bind = db.get_bind()
    event.listen(bind, "before_cursor_execute", count_statement)
    try:
        records = workhour_crud.get_all_workhours(db)
        payloads = [WorkhourFull.model_validate(record) for record in records]
    finally:
        event.remove(bind, "before_cursor_execute", count_statement)

    assert len(payloads) == 3
    assert payloads[0].user is not None
    assert payloads[0].user.department is not None
    assert payloads[0].task is not None
    assert payloads[0].task.cstshops[0].shop_number == "TPE-01"
    # One base query plus five fixed relationship queries, independent of rows.
    assert len(statements) == 6


def test_expentask_repository_update_uses_request_values(db: Session) -> None:
    created = expentask_crud.create_expentask(
        db,
        ExpenTaskCreate(expentask_name="Travel"),
    )

    updated = expentask_crud.update_expentask(
        db,
        created.id,
        ExpenTaskUpdate(expentask_name="Business travel"),
    )

    assert updated is created
    assert updated.expentask_name == "Business travel"
    assert expentask_crud.get_expentask(db, created.id) is created


def test_expenditure_repository_crud_and_monthly_totals(db: Session) -> None:
    created = expen_crud.create_expen(
        db,
        ExpenditureCreate(
            expentask_id=3,
            date=date(2026, 8, 17),
            price=500,
            description="Train ticket",
        ),
        user_id=12,
    )
    expen_crud.create_expen(
        db,
        ExpenditureCreate(
            expentask_id=3,
            date=date(2026, 8, 18),
            price=250,
            description="Taxi",
        ),
        user_id=12,
    )

    assert expen_crud.get_expen(db, created.id) is created
    assert len(expen_crud.get_expens(db, user_id=12)) == 2
    assert expen_crud.get_monthlyexpens_by_user_id(db, 12) == [
        {"year_month": "2026-08", "total_pric": 750}
    ]

    updated = expen_crud.update_expen(
        created.id,
        ExpenditureUpdate(
            expentask_id=3,
            date=date(2026, 8, 17),
            price=600,
            description="Updated train ticket",
        ),
        db,
        user_id=12,
    )
    assert updated is created
    assert updated.user_id == 12
    assert updated.price == 600

    assert expen_crud.delete_expen(created.id, db) is True
    assert expen_crud.get_expen(db, created.id) is None


@pytest.mark.parametrize(
    "delete_record",
    [
        task_crud.delete_task,
        workhour_crud.delete_workhour,
        expen_crud.delete_expen,
    ],
)
def test_delete_repositories_report_missing_records(
    db: Session,
    delete_record: Callable[[int, Session], bool],
) -> None:
    # Missing rows are a persistence result; the API layer decides the status.
    assert delete_record(999, db) is False


def test_user_detail_query_loads_current_workhour_fields(db: Session) -> None:
    department = Department(department_name="IT")
    task = Task(taskname="Support")
    user = User(
        username="thomas",
        fullname="Thomas",
        password="test-hash",
        department=department,
    )
    workhour = Workhour(
        user=user,
        task=task,
        start_date=date(2026, 8, 17),
        hour=8,
        overtime_hour=1,
    )
    db.add(workhour)
    db.commit()

    users_with_workhours = user_crud.get_allusers_monthly(db)
    payload = DataTotal.model_validate(users_with_workhours[0]).model_dump()

    assert payload["department"]["department_name"] == "IT"
    # The API keeps `date` for the current Vue client although the ORM uses
    # the corrected `start_date` attribute internally.
    assert payload["workhours"][0]["date"] == date(2026, 8, 17)
    assert payload["workhours"][0]["task"]["taskname"] == "Support"


def test_department_relationship_supports_multiple_users(db: Session) -> None:
    department = Department(department_name="Shared Department")
    db.add_all(
        [
            User(username="first-user", password="hash", department=department),
            User(username="second-user", password="hash", department=department),
        ]
    )
    db.commit()

    assert {user.username for user in department.users} == {
        "first-user",
        "second-user",
    }


def test_nested_response_schemas_map_current_orm_relationships(
    db: Session,
) -> None:
    department = Department(department_name="IT")
    user = User(
        username="schema-user",
        password="hash",
        department=department,
    )
    task = Task(
        taskname="schema-task",
        fullname="Schema task",
        organization="WorkHour",
    )
    workhour = Workhour(
        user=user,
        task=task,
        start_date=date(2026, 8, 17),
        hour=8,
        overtime_hour=0,
    )
    expense_task = ExpenTask(expentask_name="Travel")
    expenditure = Expenditure(
        user=user,
        expentask=expense_task,
        date=date(2026, 8, 17),
        price=100,
    )
    db.add_all([workhour, expenditure])
    db.commit()

    task_payload = TaskGYBase.model_validate(task).model_dump()
    expense_task_payload = ExpenTaskFull.model_validate(expense_task).model_dump()

    assert task_payload["id"] == task.id
    assert task_payload["workhours"][0]["date"] == date(2026, 8, 17)
    assert expense_task_payload["expenditures"][0]["id"] == expenditure.id


def test_full_response_graphs_serialize_after_session_closes(db: Session) -> None:
    department = Department(department_name="Detached IT")
    user = User(
        username="detached-user",
        fullname="Detached User",
        password="hash",
        department=department,
    )
    task = Task(
        taskname="detached-task",
        fullname="Detached Task",
        organization="WorkHour",
    )
    shop = CstShop(
        shop_name="Detached shop",
        shop_number="DET-01",
        task=task,
    )
    workhour = Workhour(
        user=user,
        task=task,
        shop=shop,
        start_date=date(2026, 8, 18),
        end_date=date(2026, 8, 18),
        hour=8,
        overtime_hour=0,
        case_close=False,
        active=True,
    )
    expense_task = ExpenTask(expentask_name="Detached travel")
    expenditure = Expenditure(
        user=user,
        expentask=expense_task,
        date=date(2026, 8, 18),
        price=100,
        active=True,
    )
    db.add_all([workhour, expenditure])
    db.commit()

    bind = db.get_bind()
    lookups = (
        (task_crud.get_task, task.id, TaskFull),
        (user_crud.get_user, user.id, UserFull),
        (expen_crud.get_expen, expenditure.id, ExpenditureFull),
        (expentask_crud.get_expentask, expense_task.id, ExpenTaskFull),
    )

    for lookup, record_id, schema in lookups:
        with Session(bind) as query_session:
            record = lookup(query_session, record_id)
            assert record is not None

        # Validation happens after Session.close(); no lazy SQL is possible.
        schema.model_validate(record)
