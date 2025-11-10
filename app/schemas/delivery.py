from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models import DeliveryAgentStatus


class DeliveryAgentBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    current_location: Optional[str] = None


class DeliveryAgentCreate(DeliveryAgentBase):
    pass


class DeliveryAgentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    current_location: Optional[str] = None
    active_status: Optional[DeliveryAgentStatus] = None


class DeliveryAgentResponse(DeliveryAgentBase):
    id: int
    active_status: DeliveryAgentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeliveryAgentListResponse(BaseModel):
    agents: List[DeliveryAgentResponse]
    total: int
    page: int
    size: int
    pages: int


class DeliveryStats(BaseModel):
    total_agents: int
    active_agents: int
    busy_agents: int
    inactive_agents: int
    total_deliveries: int
    completed_deliveries: int
    pending_deliveries: int
