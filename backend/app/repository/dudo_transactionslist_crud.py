from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import TransactionsList
from ..schemas import dudo_transactionslist


def get_transactionslists(db: Session, skip: int = 0):
    return db.query(TransactionsList).offset(skip).all()


def get_transactionslist_by_shop(db: Session, shop_id, search_date_start, search_date_end, skip: int = 0):
    return db.query(TransactionsList).filter(
        TransactionsList.shop_id == shop_id).filter(
            TransactionsList.create_time >= search_date_start).filter(
                TransactionsList.create_time <= search_date_end
            ).offset(skip).all()

