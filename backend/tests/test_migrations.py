from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import DateTime, create_engine, inspect, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TABLES = {
    "alembic_version",
    "branch_list",
    "cst_shop",
    "daysoff",
    "department",
    "expenditure",
    "expentask",
    "fetnetlist",
    "ipcamlist",
    "serverlist",
    "task",
    "transactions",
    "user",
    "workhour",
}
AUDITED_TABLES = {
    "department",
    "task",
    "user",
    "expentask",
    "workhour",
    "expenditure",
    "daysoff",
}


def _config(database_url: str) -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_migrations_upgrade_and_downgrade(tmp_path, monkeypatch):
    database_path = tmp_path / "migration-test.db"
    database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = _config(database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == EXPECTED_TABLES

    for table_name in AUDITED_TABLES:
        column_types = {
            column["name"]: column["type"]
            for column in inspector.get_columns(table_name)
        }
        assert isinstance(column_types["created_at"], DateTime)
        assert isinstance(column_types["updated_at"], DateTime)

    with engine.connect() as connection:
        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
    assert revision == "20260908_04"

    # Keep typed ORM refactors from silently drifting away from the migration
    # history used by existing deployments and fresh installations.
    command.check(config)
    engine.dispose()

    command.downgrade(config, "base")

    engine = create_engine(database_url)
    remaining_tables = set(inspect(engine).get_table_names())
    assert remaining_tables <= {"alembic_version"}
    engine.dispose()
