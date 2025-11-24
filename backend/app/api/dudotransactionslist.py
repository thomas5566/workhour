from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas import dudo_transactionslist
from ..database import get_db
from ..repository import dudo_transactionslist_crud

router = APIRouter(
    prefix="/transactionslist",
    tags=["TransactionsList"],
)


@router.get("/", response_model=List[dudo_transactionslist.TransactionsList])
def read_transactionslist(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactionslist_items = dudo_transactionslist_crud.get_transactionslists(db, skip=skip)
    return transactionslist_items


@router.get("/transactionslist-shopid", response_model=List[dudo_transactionslist.TransactionsListByShopId])
def read_transactionslist_by_shopid(shop_id: int = None, search_date_start: str = None, search_date_end: str = None, db: Session = Depends(get_db)):
    db_get_transactionslist_by_shopid = dudo_transactionslist_crud.get_transactionslist_by_shop(db, shop_id, search_date_start, search_date_end)
    
    if db_get_transactionslist_by_shopid is None:
        raise HTTPException(status_code=404, detail="Get transactions list by shop is not found")
    return db_get_transactionslist_by_shopid

