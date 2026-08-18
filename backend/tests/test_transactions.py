from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repository.transaction import commit_or_rollback


def test_commit_or_rollback_keeps_successful_session() -> None:
    db = Mock(spec=Session)

    commit_or_rollback(db)

    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()


def test_commit_or_rollback_restores_failed_session() -> None:
    db = Mock(spec=Session)
    failure = IntegrityError("INSERT", {}, Exception("constraint failed"))
    db.commit.side_effect = failure

    with pytest.raises(IntegrityError) as error:
        commit_or_rollback(db)

    assert error.value is failure
    db.rollback.assert_called_once_with()
