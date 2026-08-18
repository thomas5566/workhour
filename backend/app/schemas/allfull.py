from pydantic import Field

from .cstshop import CstShop
from .expens import Expenditure
from .expentasks import ExpenTask
from .tasks import Task
from .users import User
from .workhours import Workhour


class WorkhourFull(Workhour):
    user: User | None = None
    task: Task | None = None
    shop: CstShop | None = None


class ExpenditureFull(Expenditure):
    user: User | None = None
    expentask: ExpenTask | None = None


class ExpenTaskFull(ExpenTask):
    # Keep the public JSON name while reading the ORM's legacy `expens` name.
    expenditures: list[ExpenditureFull] = Field(
        default_factory=list,
        validation_alias="expens",
    )


class TaskFull(Task):
    workhours: list[WorkhourFull] = Field(default_factory=list)


class UserFull(User):
    workhours: list[WorkhourFull] = Field(default_factory=list)
