from pydantic import BaseModel, EmailStr, Field

from app.models import Order

class OrderCreate(BaseModel):
    customer_email: EmailStr
    product_name: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

class OrderStatusUpdate(BaseModel):
    status: str = Field(pattern="^(Pending|Processing|Shipped|Completed|Canceled)$")

class OrderResponse(BaseModel):
    status: str
    message:str
    data: Order