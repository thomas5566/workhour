from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.expens import ExpenditureCreate
from app.schemas.expentasks import ExpenTaskCreate
from app.schemas.fetnetlist import FetnetListUpdate
from app.schemas.ipcamlist import IpCamListUpdate
from app.schemas.serverlist import ServerListUpdate
from app.schemas.tasks import TaskCreate
from app.schemas.users import User, UserCreate
from app.schemas.workhours import Workhour, WorkhourCreate


def valid_workhour() -> dict[str, object]:
    return {
        "task_id": 1,
        "shop_id": 1,
        "start_date": date(2026, 8, 17),
        "hour": 8,
        "description": "Routine maintenance",
        "case_close": False,
        "overtime_hour": 0,
        "end_date": date(2026, 8, 17),
    }


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("task_id", 0),
        ("shop_id", -1),
        ("hour", -0.01),
        ("hour", 100),
        ("overtime_hour", 100),
        ("description", "x" * 256),
    ],
)
def test_workhour_rejects_values_outside_database_limits(
    field: str,
    invalid_value: object,
) -> None:
    payload = valid_workhour()
    payload[field] = invalid_value

    with pytest.raises(ValidationError):
        WorkhourCreate.model_validate(payload)


def test_workhour_rejects_end_date_before_start_date() -> None:
    payload = valid_workhour()
    payload["end_date"] = date(2026, 8, 16)

    with pytest.raises(ValidationError, match="end_date must be on or after start_date"):
        WorkhourCreate.model_validate(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"expentask_id": 0, "date": date(2026, 8, 17), "price": 100},
        {"expentask_id": 1, "date": date(2026, 8, 17), "price": -1},
        {
            "expentask_id": 1,
            "date": date(2026, 8, 17),
            "price": 100,
            "description": "x" * 256,
        },
    ],
)
def test_expenditure_rejects_invalid_values(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ExpenditureCreate.model_validate(payload)


@pytest.mark.parametrize(
    ("schema", "payload"),
    [
        (
            TaskCreate,
            {"taskname": "", "fullname": "Task", "organization": "Operations"},
        ),
        (ExpenTaskCreate, {"expentask_name": "x" * 256}),
        (
            UserCreate,
            {
                "username": "operator",
                "fullname": "Operator",
                "password": "secure-password",
                "department_id": 0,
            },
        ),
    ],
)
def test_core_write_schemas_reject_invalid_values(
    schema: type[TaskCreate] | type[ExpenTaskCreate] | type[UserCreate],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        schema.model_validate(payload)


def test_task_create_rejects_retired_relationship_input() -> None:
    with pytest.raises(ValidationError, match="cstshops"):
        TaskCreate.model_validate(
            {
                "taskname": "TASK-001",
                "fullname": "Task",
                "organization": "Operations",
                "cstshops": [],
            }
        )


def test_read_schemas_tolerate_nullable_legacy_rows() -> None:
    # Existing databases permit NULL in columns that modern create schemas require.
    assert User.model_validate({"id": 1}).username is None
    workhour = Workhour.model_validate({"id": 1})
    assert workhour.task_id is None
    assert workhour.start_date is None


def test_user_create_enforces_bcrypt_utf8_byte_limit() -> None:
    valid_payload = {
        "username": "utf8-user",
        "fullname": "UTF-8 User",
        "password": "x" * 72,
        "department_id": 1,
    }
    assert UserCreate.model_validate(valid_payload).username == "utf8-user"

    with pytest.raises(ValidationError, match="72 UTF-8 bytes"):
        UserCreate.model_validate({**valid_payload, "password": "密" * 25})


def valid_server_update() -> dict[str, object]:
    return {
        "server_name": "Application server",
        "server_ip": "192.0.2.10",
        "server_location": "Taipei",
        "server_acc": "operator",
        "server_pass": "credential",
        "server_remark": "Primary",
    }


def valid_fetnet_update() -> dict[str, object]:
    return {
        "shop_id": 1,
        "shop_name": "Taipei shop",
        "shop_tax": "12345678",
        "shop_location": "Taipei",
        "shop_phone_number": "02-1234-5678",
        "shop_phone_short_code": "1234",
        "adsl_number": "ADSL-001",
        "fetnet_phone_number": "0912-345-678",
        "adsl_bank_number": "BANK-001",
        "fetnetlist_remark": "Primary line",
    }


def valid_ipcam_update() -> dict[str, object]:
    return {
        "shop_id": 1,
        "shop_name": "Taipei shop",
        "ipcam_brand": "Camera brand",
        "ipcam_ip": "192.0.2.20",
        "admin_acc": "admin",
        "admin_pass": "admin credential",
        "user_acc": "viewer",
        "user_pass": "viewer credential",
        "phone_port": "8000",
        "http_port": "80",
        "tcp_port": "9000",
        "remark": "Entrance",
    }


@pytest.mark.parametrize(
    ("schema", "payload", "field", "invalid_value"),
    [
        (ServerListUpdate, valid_server_update(), "server_name", "x" * 256),
        (FetnetListUpdate, valid_fetnet_update(), "shop_id", 0),
        (FetnetListUpdate, valid_fetnet_update(), "shop_location", "x" * 256),
        (IpCamListUpdate, valid_ipcam_update(), "shop_id", -1),
        (IpCamListUpdate, valid_ipcam_update(), "remark", "x" * 256),
    ],
)
def test_inventory_updates_reject_values_outside_database_limits(
    schema: type[ServerListUpdate] | type[FetnetListUpdate] | type[IpCamListUpdate],
    payload: dict[str, object],
    field: str,
    invalid_value: object,
) -> None:
    payload[field] = invalid_value

    with pytest.raises(ValidationError):
        schema.model_validate(payload)
