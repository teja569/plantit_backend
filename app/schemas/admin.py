from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date


class DashboardStats(BaseModel):
    total_users: int
    total_sellers: int
    total_plants: int
    total_orders: int
    total_revenue: float
    active_delivery_agents: int
    pending_orders: int
    verified_plants: int


class UserStats(BaseModel):
    total_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    verified_users: int
    active_users: int


class PlantStats(BaseModel):
    total_plants: int
    verified_plants: int
    unverified_plants: int
    plants_by_category: Dict[str, int]
    top_selling_plants: List[Dict[str, Any]]


class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    confirmed_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float


class RevenueStats(BaseModel):
    total_revenue: float
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float
    revenue_by_month: List[Dict[str, Any]]


class TopSeller(BaseModel):
    seller_id: int
    seller_name: str
    total_sales: float
    total_orders: int
    plants_sold: int


class AdminDashboard(BaseModel):
    stats: DashboardStats
    user_stats: UserStats
    plant_stats: PlantStats
    order_stats: OrderStats
    revenue_stats: RevenueStats
    top_sellers: List[TopSeller]
    recent_orders: List[Dict[str, Any]]
    recent_plants: List[Dict[str, Any]]


class SystemHealth(BaseModel):
    database_status: str
    ml_model_status: str
    storage_status: str
    redis_status: str
    uptime: str


class AnnouncementCreate(BaseModel):
    title: str
    message: str
    audience: str | None = None


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    message: str
    audience: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True