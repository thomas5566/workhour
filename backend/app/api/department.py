from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List


from .. import schemas
from ..database import get_db
from ..repository import department_crud


router = APIRouter(
    prefix="/department",
    tags=["Department"],
)

@router.get("/", response_model=List[schemas.Department])
def read_departments(db: Session = Depends(get_db)):
    departments = department_crud.get_departments(db)
    if departments is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Departments not found")
    return departments