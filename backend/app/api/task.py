from fastapi import APIRouter, HTTPException, status

from ..auth import CurrentUser, ManagerUser
from ..repository import task_crud
from ..schemas import allfull, tasks
from .dependencies import DatabaseSession, PageLimit, PageOffset, PositivePathId

router = APIRouter(
    prefix="/task",
    tags=["Task"],
)


@router.post("/", response_model=tasks.Task)
def create_task(
    task_items: tasks.TaskCreate,
    db: DatabaseSession,
    manager: ManagerUser,
):
    db_task = task_crud.get_task_by_taskname(db, taskname=task_items.taskname)
    if db_task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task name already registered",
        )
    return task_crud.create_task(db=db, task_items=task_items)


@router.get("/", response_model=list[tasks.Task])
def read_tasks(
    db: DatabaseSession,
    user: CurrentUser,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    return task_crud.get_tasks(db, skip=skip, limit=limit)


@router.get("/tasksgbw/", response_model=list[tasks.TaskGYBase])
def read_tasks_groupby_worklist(
    db: DatabaseSession,
    manager: ManagerUser,
):
    return task_crud.get_tasks_by_worklist(db)


@router.get("/{task_id}", response_model=allfull.TaskFull)
def read_task(
    task_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
):
    db_task = task_crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=allfull.TaskFull)
def edit_task(
    task_items: tasks.TaskUpdate,
    task_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
):
    db_task = task_crud.update_task(db, task_id=task_id, task_items=task_items)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
) -> None:
    if not task_crud.delete_task(task_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
