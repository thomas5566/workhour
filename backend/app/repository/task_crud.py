from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager, selectinload

from ..models import Task, User, Workhour
from ..schemas import tasks
from .transaction import commit_or_rollback


def get_task(db: Session, task_id: int) -> Task | None:
    statement = (
        select(Task)
        .options(
            selectinload(Task.cstshops),
            selectinload(Task.workhours)
            .selectinload(Workhour.user)
            .selectinload(User.department),
            selectinload(Task.workhours)
            .selectinload(Workhour.task)
            .selectinload(Task.cstshops),
            selectinload(Task.workhours).selectinload(Workhour.shop),
        )
        .where(Task.id == task_id)
    )
    return db.scalar(statement)


def get_task_by_taskname(db: Session, taskname: str) -> Task | None:
    return db.scalar(select(Task).where(Task.taskname == taskname))


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    statement = (
        select(Task)
        .options(selectinload(Task.cstshops))
        .where(Task.is_active.is_(True))
        .order_by(Task.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_tasks_by_worklist(db: Session) -> list[Task]:
    statement = (
        select(Task)
        .join(Task.workhours)
        .join(Workhour.user)
        .options(
            contains_eager(Task.workhours).contains_eager(Workhour.user)
        )
        .order_by(Workhour.start_date.desc(), Workhour.id.desc())
    )
    return list(db.execute(statement).unique().scalars().all())


def create_task(db: Session, task_items: tasks.TaskCreate) -> Task:
    db_task = Task(
        taskname=task_items.taskname,
        fullname=task_items.fullname,
        organization=task_items.organization,
    )
    db.add(db_task)
    commit_or_rollback(db)
    db.refresh(db_task)
    return db_task


def update_task(
    db: Session,
    task_id: int,
    task_items: tasks.TaskUpdate,
) -> Task | None:
    db_task = get_task(db, task_id)
    if db_task is None:
        return None

    db_task.taskname = task_items.taskname
    db_task.fullname = task_items.fullname
    db_task.organization = task_items.organization
    commit_or_rollback(db)
    db.refresh(db_task)
    return db_task


def delete_task(task_id: int, db: Session) -> bool:
    task_item = get_task(db, task_id)
    if task_item is None:
        # Repositories report persistence outcomes; routes own HTTP semantics.
        return False

    db.delete(task_item)
    commit_or_rollback(db)
    return True
