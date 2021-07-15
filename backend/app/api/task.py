from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
# from app import crud, schemas, config
# from .. import schemas

from ..schemas import tasks, allfull
from ..database import get_db
from ..repository import task_crud
from ..auth import login_manager

router = APIRouter(
    prefix="/task",
    tags=["Task"],
)


@router.post("/", response_model=tasks.Task)
def create_task(task_items: tasks.TaskCreate, db: Session = Depends(get_db)):
    db_task = task_crud.get_task_by_taskname(db, taskname=task_items.taskname)
    if db_task:
        raise HTTPException(
            status_code=400, detail="Taskname already registered")
    return task_crud.create_task(db=db, task_items=task_items)


@router.get("/", response_model=List[tasks.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks_items = task_crud.get_tasks(db, skip=skip, limit=limit)
    return tasks_items


@router.get("/tasksgbw", response_model=List[tasks.TaskGYBase])
def read_tasks_groupby_worklist(db: Session = Depends(get_db), user=Depends(login_manager)):
    user_dp = user.department_id
    list_dp_p = user.checklistAll_permission
    print("department_id:", user_dp)
    print("permission:", list_dp_p)
    # print(current_user.is_superuser)
    if list_dp_p == 2:
        tasks_items = task_crud.get_tasks_by_worklist(db)
        return tasks_items
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not permitted!!")


@router.get("/{task_id}", response_model=allfull.TaskFull)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task_crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=allfull.TaskFull)
def edit_task(task_items: tasks.TaskUpdate, task_id: int, db: Session = Depends(get_db)):
    db_task = task_crud.update_task(db, task_id=task_id, task_items=task_items)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.delete("/{id}", response_class=Response)
def delete_task(id: int, db: Session = Depends(get_db)):
    # expen.user_id = user.id
    return task_crud.delete_task(id, db)
