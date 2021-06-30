from typing import List, Optional

from .users import User
from .expens import Expenditure
from .expentasks import ExpenTask
from .tasks import Task
from .whorkhours import Workhour


class WorkhourFull(Workhour):
    user: Optional[User]
    task: Optional[Task]


class ExpenditureFull(Expenditure):
    user: Optional[User]
    expentask: Optional[ExpenTask]


class ExpenTaskFull(ExpenTask):
    expenditures: List[ExpenditureFull] = []


class TaskFull(Task):
    workhours: List[WorkhourFull] = []


class UserFull(User):
    workhours: List[WorkhourFull] = []
