from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import require_admin, get_current_active_user
from app.schemas.delivery import (
    DeliveryAgentCreate, DeliveryAgentResponse, DeliveryAgentUpdate,
    DeliveryAgentListResponse, DeliveryStats
)
from app.services.delivery_service import DeliveryService
from app.models import DeliveryAgentStatus, OrderStatus, User

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.post("/agents", response_model=DeliveryAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_agent(
    agent_data: DeliveryAgentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new delivery agent (admin only)"""
    delivery_service = DeliveryService(db)
    agent = delivery_service.create_delivery_agent(agent_data)
    return agent


@router.get("/agents", response_model=DeliveryAgentListResponse)
async def get_delivery_agents(
    page: int = 1,
    size: int = 20,
    status: DeliveryAgentStatus = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get delivery agents (admin only)"""
    delivery_service = DeliveryService(db)
    agents, total = delivery_service.get_delivery_agents(page, size, status)
    pages = (total + size - 1) // size
    
    return DeliveryAgentListResponse(
        agents=agents,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/agents/{agent_id}", response_model=DeliveryAgentResponse)
async def get_delivery_agent(
    agent_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get delivery agent by ID (admin only)"""
    delivery_service = DeliveryService(db)
    agent = delivery_service.get_delivery_agent_by_id(agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    return agent


@router.put("/agents/{agent_id}", response_model=DeliveryAgentResponse)
async def update_delivery_agent(
    agent_id: int,
    agent_data: DeliveryAgentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update delivery agent (admin only)"""
    delivery_service = DeliveryService(db)
    agent = delivery_service.update_delivery_agent(agent_id, agent_data)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    return agent


@router.put("/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: int,
    status: DeliveryAgentStatus,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update delivery agent status (admin only)"""
    delivery_service = DeliveryService(db)
    success = delivery_service.update_agent_status(agent_id, status)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    return {"message": f"Agent status updated to {status}"}


@router.get("/agents/{agent_id}/orders")
async def get_agent_orders(
    agent_id: int,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get orders assigned to delivery agent (admin only)"""
    delivery_service = DeliveryService(db)
    orders, total = delivery_service.get_agent_orders(agent_id, page, size)
    pages = (total + size - 1) // size
    
    return {
        "orders": orders,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }


@router.get("/agents/available")
async def get_available_agents(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get available delivery agents (admin only)"""
    delivery_service = DeliveryService(db)
    agents = delivery_service.get_available_agents()
    return {"available_agents": agents}


@router.post("/orders/{order_id}/assign")
async def assign_order_to_agent(
    order_id: int,
    agent_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign order to delivery agent (admin only)"""
    delivery_service = DeliveryService(db)
    success = delivery_service.assign_order_to_agent(order_id, agent_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order or agent not found"
        )
    
    return {"message": "Order assigned to delivery agent successfully"}


@router.put("/orders/{order_id}/complete")
async def complete_delivery(
    order_id: int,
    agent_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mark delivery as completed (admin only)"""
    delivery_service = DeliveryService(db)
    success = delivery_service.complete_delivery(order_id, agent_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or not assigned to agent"
        )
    
    return {"message": "Delivery marked as completed"}


@router.get("/stats", response_model=DeliveryStats)
async def get_delivery_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get delivery statistics (admin only)"""
    delivery_service = DeliveryService(db)
    stats = delivery_service.get_delivery_stats()
    return stats
