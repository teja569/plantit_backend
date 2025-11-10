from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models import OrderStatus


class OrderItemCreate(BaseModel):
    plant_id: int
    quantity: int


class OrderCreate(BaseModel):
    seller_id: int
    items: List[OrderItemCreate]
    shipping_address: str
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_agent_id: Optional[int] = None
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    plant_id: int
    quantity: int
    unit_price: float
    plant_name: str
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    delivery_agent_id: Optional[int] = None
    status: OrderStatus
    total_price: float
    shipping_address: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    size: int
    pages: int


class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    total_revenue: float


class PaymentMethod(str):
    COD = "cod"
    RAZORPAY = "razorpay"


class CheckoutRequest(BaseModel):
    shipping_address: str
    notes: Optional[str] = None
    payment_method: str  # "cod" or "razorpay"


class CheckoutOrderSummary(BaseModel):
    order_id: int
    seller_id: int
    total_price: float
    status: OrderStatus


class CheckoutResponse(BaseModel):
    orders: List[CheckoutOrderSummary]
    payment_required: bool
    payment_provider: Optional[str] = None
    payment_payload: Optional[dict] = None