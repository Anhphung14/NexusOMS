from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Order(SQLModel, table = True):
    __tablename__ = "order"
    id: Optional[int] = Field(default = None, primary_key=True)
    customer_email: str = Field(index = True, max_length = 100)
    product_name: str = Field(index = True, max_length = 255)
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)
    status: str = Field(default = "Pending", max_length=100)
    created_at: datetime = Field(default_factory = datetime.utcnow)
