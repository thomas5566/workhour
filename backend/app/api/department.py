from fastapi import APIRouter, Depends

from ..auth import login_manager
from ..repository import department_crud
from ..schemas import departments
from .dependencies import DatabaseSession

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
