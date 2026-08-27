from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import login_manager, require_manager
from ..repository import department_crud
from ..schemas import departments
from .dependencies import DatabaseSession, PositivePathId

router = APIRouter(
    prefix="/department",
    tags=["Department"],
    # Department names are internal organization metadata. Protecting the
    # router also keeps future department endpoints authenticated by default.
    dependencies=[Depends(login_manager)],
)


@router.get("/", response_model=list[departments.Department])
def read_departments(db: DatabaseSession):
    # Collection endpoints use an empty list as the canonical no-data response.
    return department_crud.get_departments(db)


@router.post(
    "/",
    response_model=departments.Department,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_manager)],
)
def create_department(payload: departments.DepartmentWrite, db: DatabaseSession):
    return department_crud.create_department(db, payload)


@router.put(
    "/{department_id}",
    response_model=departments.Department,
    dependencies=[Depends(require_manager)],
)
def update_department(
    department_id: PositivePathId,
    payload: departments.DepartmentWrite,
    db: DatabaseSession,
):
    record = department_crud.get_department_by_id(db, department_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department_crud.update_department(db, record, payload)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_manager)],
)
def delete_department(department_id: PositivePathId, db: DatabaseSession) -> None:
    record = department_crud.get_department_by_id(db, department_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Department not found")
    department_crud.delete_department(db, record)
