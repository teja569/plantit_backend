from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class SellerDashboard(BaseModel):
    total_plants: int
    active_plants: int
    total_orders: int
    pending_orders: int
    completed_orders: int
    total_revenue: float
    monthly_revenue: float
    top_selling_plants: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]


class SellerStats(BaseModel):
    total_plants: int
    verified_plants: int
    total_orders: int
    total_revenue: float
    average_order_value: float
    conversion_rate: float


class SellerOnboarding(BaseModel):
    business_name: str
    business_type: str
    tax_id: Optional[str] = None
    business_address: str
    business_phone: str
    business_email: str
    description: Optional[str] = None


class SellerProfile(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    description: Optional[str] = None
    is_verified: bool = False


class SellerEarnings(BaseModel):
    total_earnings: float
    pending_earnings: float
    available_earnings: float
    earnings_this_month: float
    earnings_by_month: List[Dict[str, Any]]
