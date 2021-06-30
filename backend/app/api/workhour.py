from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
# from app import crud, schemas, config
# from .. import schemas

from ..schemas import whorkhours, allfull
from ..repository import workhour_crud
from ..database import get_db
from ..auth import login_manager

router = APIRouter(
    prefix="/workhour",
    tags=["Workhour"],
)


@router.post("/", response_model=allfull.WorkhourFull)
def create_workhour(workhour_items: whorkhours.WorkhourCreate, db: Session = Depends(get_db), user=Depends(login_manager)):
    workhour_items.user_id = user.id
    return workhour_crud.create_workhour(db=db, workhour_items=workhour_items)


@router.get("/workhours", response_model=List[allfull.WorkhourFull])
def read_workhours(db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    return workhour_crud.get_workhours(db, user_id)

# @router.get("/worklist-group", response_model=List[schemas.WorkhourFull])
# def read_workhours(user: schemas.User, db: Session = Depends(get_db)):
#     group = user.department
#     return workhour_crud.get_worklist_by_group(db, group)


# def read_workhours(skip: int = 0, limit: int = 100, user_id: int = None, task_id: int = None, db: Session = Depends(get_db)):
#     if user_id and task_id:
#         workhours = workhour_crud.get_workhours_by_user_task(db, skip=skip, limit=limit, user_id=user_id, task_id=task_id)
#     elif user_id:
#         workhours = workhour_crud.get_workhours_by_user_id(db, skip=skip, limit=limit, user_id=user_id)
#     elif task_id:
#         workhours = workhour_crud.get_workhours_by_task_id(db, skip=skip, limit=limit, task_id=task_id)
#     else:
#         workhours = workhour_crud.get_workhours(db, skip=skip, limit=limit)
#     return workhours

@router.get('/my/{user_id}', response_model=List[allfull.WorkhourFull])
def read_workhours_my(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(login_manager)):
    # user_id = user.id
    list_dp_p = user.checklistAll_permission
    if list_dp_p == 1:
        workhours = workhour_crud.get_workhours_by_user_id(
            db, skip=skip, limit=limit, user_id=user_id)
        return workhours
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not permitted!!")
    # workhours = workhour_crud.get_workhours_by_user_id(
    #     db, skip=skip, limit=limit, user_id=user_id)
    # return workhours


@router.get('/totalhour/{user_id}', response_model=List[whorkhours.WorkhourTotal])
def get_totalworkhours_byid(user_id: int, db: Session = Depends(get_db), user=Depends(login_manager)):
    # user_id = 5
    list_dp_p = user.checklistAll_permission
    if list_dp_p == 1:
        workhour_items = workhour_crud.get_monthlyworkhours_by_user_id(
            db, user_id=user_id)
        return workhour_items
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not permitted!!")
    # workhour_items = workhour_crud.get_monthlyworkhours_by_user_id(
    #     db, user_id=user_id)
    # print(workhour_items)
    # return workhour_items


@router.get("/{workhour_id}", response_model=allfull.WorkhourFull)
def read_workhour(workhour_id: int, db: Session = Depends(get_db)):
    db_workhour = workhour_crud.get_workhour(db, workhour_id=workhour_id)
    if db_workhour is None:
        raise HTTPException(status_code=404, detail="Workhour not found")
    return db_workhour

# @router.put("/{workhour_id}", response_model=schemas.WorkhourFull)
# def edit_workhour(workhour: schemas.WorkhourUpdate, workhour_id: int, db: Session = Depends(get_db)):
#     # user_id = user.id
#     db_workhour = workhour_crud.update_workhour(db, workhour_id=workhour_id, workhour=workhour)
#     if db_workhour is None:
#         raise HTTPException(status_code=404, detail="Workhour not found")
#     return db_workhour


@router.put("/{workhour_id}")
def edit_workhour(workhour_id: int, workhour_items: whorkhours.WorkhourUpdate, db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    workhour_retrieved = workhour_crud.get_workhour(
        db=db, workhour_id=workhour_id)
    if not workhour_retrieved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Workhour with id {id} does not exist")
    if workhour_retrieved.user_id == user.id:
        message = workhour_crud.update_workhour(
            workhour_id=workhour_id, workhour_items=workhour_items, db=db, user_id=user_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You are not authorized to update.")
    return {"detail": "Successfully updated data."}

# @router.get("/totalhours", response_model=List[schemas.WorkhourFull])
# def read_totalworkhours(skip: int=0, db: Session = Depends(get_db)):
#     totalworkhours = crud.get_totalworkhours_by_user_id(db, skip=skip)
#     list_totalhours = [int(number) for number in totalworkhours]
#     return list_totalhours


@router.delete("/{id}", response_class=Response)
def delete_workhour(id: int, db: Session = Depends(get_db)):
    # expen.user_id = user.id
    return workhour_crud.delete_workhour(id, db)
