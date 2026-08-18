import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-characters")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
