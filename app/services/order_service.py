from sqlmodel import Session, select

from app.models.order import Order
from app.schemas.order import OrderCreate


def create_order(db: Session, data: OrderCreate):
    order = Order(**data.model_dump())

    db.add(order)
    db.commit()
    db.refresh(order)

    return order

def get_orders(db: Session, skip: int, limit: int):
    statement = select(Order).offset(skip).limit(limit)

    return db.exec(statement).all()

def get_order_by_id(db: Session, order_id: int):
    return db.get(Order, order_id)

def update_status(db: Session, order:Order, status: str):
    order.status = status

    db.add(order)
    db.commit()
    db.refresh(order)

    return order