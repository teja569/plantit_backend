from pydantic import BaseModel
from typing import Optional


class RazorpayOrderRequest(BaseModel):
    order_id: int


class RazorpayOrderResponse(BaseModel):
    provider: str = "razorpay"
    amount: float
    currency: str = "INR"
    provider_order_id: str
    receipt: str


class RazorpayWebhookPayload(BaseModel):
    provider_order_id: str
    provider_payment_id: str
    provider_signature: Optional[str] = None
    status: str


class CODConfirmRequest(BaseModel):
    order_id: int


