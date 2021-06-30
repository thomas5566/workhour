from fastapi import APIRouter, Depends, HTTPException
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
    tasks = task_crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@router.get("/{task_id}", response_model=allfull.TaskFull)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task_crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=allfull.TaskFull)
def edit_workhour(task_items: tasks.TaskUpdate, task_id: int, db: Session = Depends(get_db)):
    db_task = task_crud.update_task(db, task_id=task_id, task_items=task_items)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
