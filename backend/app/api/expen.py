from fastapi import APIRouter, Depends, HTTPException, status, Response
# from starlette.status import HTTP_404_NOT_FOUND
from sqlalchemy.orm import Session, session
from typing import List
# from app import crud, schemas, config
# from .. import schemas, models, oauth2

from ..schemas import expens, allfull
from ..database import get_db
from ..repository import expen_crud
from ..auth import login_manager
# from .route_login import get_current_user_from_token


router = APIRouter(
    prefix="/expen",
    tags=["Expens"],
)


@router.post("/", response_model=allfull.ExpenditureFull)
def create_expen(expen_item: expens.ExpenditureCreate, db: Session = Depends(get_db),
                 user=Depends(login_manager)):
    expen_item.user_id = user.id
    return expen_crud.create_expen(db=db, expen_item=expen_item)


@router.get("/expens", response_model=List[allfull.ExpenditureFull])
def read_expens(db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    return expen_crud.get_expens(db, user_id)


@router.get('/my/{user_id}', response_model=List[allfull.ExpenditureFull])
def read_expens_my(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(login_manager)):
    # user_id = user.id
    list_dp_p = user.checklistAll_permission
    if list_dp_p == 1:
        expens = expen_crud.get_expens_by_user_id(
            db, skip=skip, limit=limit, user_id=user_id)
        return expens
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not permitted!!")
# def read_expens(skip: int = 0, limit: int = 100, user_id: int = None,
#                 expen_id: int = None, db: Session = Depends(get_db)):
#     if user_id and expen_id:
#         expens = expen_crud.get_expens_by_user_expentask(
#             db, skip=skip, limit=limit, user_id=user_id, expen_id=expen_id)
#     elif user_id:
#         expens = expen_crud.get_expens_by_user_id(
#             db, skip=skip, limit=limit, user_id=user_id)
#     elif expen_id:
#         expens = expen_crud.get_expens_by_expentask_id(
#             db, skip=skip, limit=limit, expen_id=expen_id)
#     else:
#         expens = expen_crud.get_expens(db, skip=skip, limit=limit)
#     return expens


@router.get('/totalexpen/{user_id}', response_model=List[expens.ExpenTotal])
def get_totalexpens_byid(user_id: int, db: Session = Depends(get_db), user=Depends(login_manager)):
    # user_id = 5
    list_dp_p = user.checklistAll_permission
    if list_dp_p == 1:
        expen_items = expen_crud.get_monthlyexpens_by_user_id(
            db, user_id=user_id)
        return expen_items
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not permitted!!")
    # expen_items = expen_crud.get_monthlyexpens_by_user_id(
    #     db, user_id=user_id)
    # print(expen_items)
    # return expen_items


@router.get("/{expen_id}", response_model=allfull.ExpenditureFull)
def read_expen(expen_id: int, db: Session = Depends(get_db),
               user=Depends(login_manager)):
    db_expen = expen_crud.get_expen(db, expen_id=expen_id)
    if db_expen is None:
        raise HTTPException(status_code=404, detail="Expen not found")
    return db_expen


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_expen(id: int, request: expens.Expenditure,
                 db: Session = Depends(get_db)):
    return expen_crud.update_expen(id, request, db)


@router.delete("/{id}", response_class=Response)
def delete_expen(id: int, db: Session = Depends(get_db)):
    # expen.user_id = user.id
    return expen_crud.delete_expen(id, db)

# @router.delete("/delete/{id}")
# def delete_expen(id: int, db: Session = Depends(get_db),
#                current_user: models.User = Depends(get_current_user_from_token)):
#     expen = expen_crud.get_expen(db=db, id=id)
#     if not expen:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Job with id {id} does not exist")
#     if expen.user_id == current_user.id:
#         expen_crud.delete_expen(id=id, db=db)
#         return {"detail":"Job Successfully deleted"}
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                         detail="You are not permitted!!")
