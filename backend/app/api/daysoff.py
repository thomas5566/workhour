from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

# from app import crud, schemas, config
# from .. import schemas
from ..auth import login_manager
from ..schemas import daysoff, allfull
from ..database import get_db
from ..repository import daysoff_crud

router = APIRouter(
    prefix="/daysoff",
    tags=["Daysoff"],
)


@router.post("/", response_model=allfull.DaysoffFull)
def create_daysoff(daysoff_items: daysoff.DaysoffCreate, db: Session = Depends(get_db)):
    # daysoff_items.user_id = user.id
    return daysoff_crud.create_daysoff(db=db, daysoff_items=daysoff_items)


@router.get("/", response_model=List[allfull.DaysoffFull])
def read_daysoff_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    daysoff_items = daysoff_crud.get_daysoff_lists(db, skip=skip, limit=limit)
    return daysoff_items


@router.get("/daysoffbyuser", response_model=List[allfull.DaysoffFull])
def read_daysoff_by_user(db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    return daysoff_crud.get_daysoff_by_userid(db, user_id)
# @router.get("/tasksgbw", response_model=List[tasks.TaskGYBase])
# def read_tasks_groupby_worklist(db: Session = Depends(get_db), user=Depends(login_manager)):
#     user_dp = user.department_id
#     list_dp_p = user.checklistAll_permission
#     print("department_id:", user_dp)
#     print("permission:", list_dp_p)
#     # print(current_user.is_superuser)
#     if list_dp_p == 2:
#         tasks_items = task_crud.get_tasks_by_worklist(db)
#         return tasks_items
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                         detail="You are not permitted!!")


@router.get("/{daysoff_id}", response_model=allfull.DaysoffFull)
def read_daysoff(daysoff_id: int, db: Session = Depends(get_db)):
    db_daysoff = daysoff_crud.get_daysoff_by_id(db, daysoff_id=daysoff_id)
    if db_daysoff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Daysoff not found")
    return db_daysoff


@router.put("/{daysoff_id}")
def edit_daysoff(daysoff_id: int, daysoff_items: daysoff.DaysoffUpdate, db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    message = daysoff_crud.update_daysoff(
        daysoff_id=daysoff_id, daysoff_items=daysoff_items, db=db, user_id=user_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Dayoff with id {daysoff_id} does not exist")
    return {"detial": "Successfully update data."}


@router.delete("/{id}", response_class=Response)
def delete_daysoff(id: int, db: Session = Depends(get_db)):
    return daysoff_crud.delete_daysoff(id, db)
