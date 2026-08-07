from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.db.database import get_session
from app.models.order import Order
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate
)

from app.services import order_service

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

@router.post("", response_model=OrderResponse)
async def create_order(
        order: OrderCreate,
        db: Session = Depends(get_session),
):
    db_order = order_service.create_order(db, order)
    return OrderResponse(
        status="success",
        message="Order created successfully",
        data=db_order,
    )

@router.get("", response_model=List[Order])
async def get_orders(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_session),
):
    return order_service.get_orders(db, skip, limit)

@router.get("/{order_id}", response_model=Order)
async def get_order(
        order_id: int,
        db: Session = Depends(get_session),
):
    order = order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

@router.patch("/{order_id}", response_model=OrderResponse, description="Update status of order")
async def update_status(
        order_id: int,
        body: OrderStatusUpdate,
        db: Session = Depends(get_session),
):
    order = order_service.get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order = order_service.update_status(db, order, body.status)
    return OrderResponse(
        status="success",
        message="Order updated successfully",
        data=order,
    )
