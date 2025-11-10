from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from app.models import DeliveryAgent, Order, OrderStatus, DeliveryAgentStatus, DeliveryTimeline
from app.schemas.delivery import DeliveryAgentCreate, DeliveryAgentUpdate, DeliveryStats
from app.core.logging import logger


class DeliveryService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_delivery_agent(self, agent_data: DeliveryAgentCreate) -> DeliveryAgent:
        """Create a new delivery agent"""
        # Check if phone number already exists
        existing_agent = self.db.query(DeliveryAgent).filter(
            DeliveryAgent.phone == agent_data.phone
        ).first()
        
        if existing_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        db_agent = DeliveryAgent(
            name=agent_data.name,
            phone=agent_data.phone,
            email=agent_data.email,
            current_location=agent_data.current_location,
            active_status=DeliveryAgentStatus.ACTIVE
        )
        
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Delivery agent {db_agent.id} created successfully")
        return db_agent
    
    def get_delivery_agent_by_id(self, agent_id: int) -> Optional[DeliveryAgent]:
        """Get delivery agent by ID"""
        return self.db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    
    def get_delivery_agents(self, page: int = 1, size: int = 20, status_filter: Optional[DeliveryAgentStatus] = None) -> Tuple[List[DeliveryAgent], int]:
        """Get delivery agents with pagination and filtering"""
        query = self.db.query(DeliveryAgent)
        
        if status_filter:
            query = query.filter(DeliveryAgent.active_status == status_filter)
        
        total = query.count()
        offset = (page - 1) * size
        agents = query.offset(offset).limit(size).all()
        
        return agents, total
    
    def update_delivery_agent(self, agent_id: int, agent_data: DeliveryAgentUpdate) -> Optional[DeliveryAgent]:
        """Update delivery agent information"""
        agent = self.get_delivery_agent_by_id(agent_id)
        if not agent:
            return None
        
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        self.db.commit()
        self.db.refresh(agent)
        
        logger.info(f"Delivery agent {agent_id} updated successfully")
        return agent
    
    def update_agent_status(self, agent_id: int, status: DeliveryAgentStatus) -> bool:
        """Update delivery agent status"""
        agent = self.get_delivery_agent_by_id(agent_id)
        if not agent:
            return False
        
        agent.active_status = status
        self.db.commit()
        
        logger.info(f"Delivery agent {agent_id} status updated to {status}")
        return True
    
    def get_agent_orders(self, agent_id: int, page: int = 1, size: int = 20) -> Tuple[List[Order], int]:
        """Get orders assigned to a delivery agent"""
        query = self.db.query(Order).filter(Order.delivery_agent_id == agent_id)
        total = query.count()
        
        offset = (page - 1) * size
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(size).all()
        
        return orders, total
    
    def get_available_agents(self) -> List[DeliveryAgent]:
        """Get available delivery agents (active and not busy)"""
        return self.db.query(DeliveryAgent).filter(
            DeliveryAgent.active_status == DeliveryAgentStatus.ACTIVE
        ).all()
    
    def assign_order_to_agent(self, order_id: int, agent_id: int) -> bool:
        """Assign order to delivery agent"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        agent = self.get_delivery_agent_by_id(agent_id)
        
        if not order or not agent:
            return False
        
        if agent.active_status != DeliveryAgentStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent is not available for delivery"
            )
        
        order.delivery_agent_id = agent_id
        order.status = OrderStatus.CONFIRMED
        try:
            self.db.add(DeliveryTimeline(order_id=order.id, status=OrderStatus.CONFIRMED.value, note="Assigned to agent"))
        except Exception:
            pass
        
        # Mark agent as busy
        agent.active_status = DeliveryAgentStatus.BUSY
        
        self.db.commit()
        
        logger.info(f"Order {order_id} assigned to delivery agent {agent_id}")
        return True
    
    def complete_delivery(self, order_id: int, agent_id: int) -> bool:
        """Mark delivery as completed"""
        order = self.db.query(Order).filter(
            Order.id == order_id,
            Order.delivery_agent_id == agent_id
        ).first()
        
        if not order:
            return False
        
        order.status = OrderStatus.DELIVERED
        try:
            self.db.add(DeliveryTimeline(order_id=order.id, status=OrderStatus.DELIVERED.value, note="Delivered"))
        except Exception:
            pass
        
        # Mark agent as available again
        agent = self.get_delivery_agent_by_id(agent_id)
        if agent:
            agent.active_status = DeliveryAgentStatus.ACTIVE
        
        self.db.commit()
        
        logger.info(f"Delivery completed for order {order_id} by agent {agent_id}")
        return True
    
    def get_delivery_stats(self) -> DeliveryStats:
        """Get delivery statistics"""
        total_agents = self.db.query(DeliveryAgent).count()
        active_agents = self.db.query(DeliveryAgent).filter(
            DeliveryAgent.active_status == DeliveryAgentStatus.ACTIVE
        ).count()
        busy_agents = self.db.query(DeliveryAgent).filter(
            DeliveryAgent.active_status == DeliveryAgentStatus.BUSY
        ).count()
        inactive_agents = self.db.query(DeliveryAgent).filter(
            DeliveryAgent.active_status == DeliveryAgentStatus.INACTIVE
        ).count()
        
        total_deliveries = self.db.query(Order).filter(
            Order.delivery_agent_id.isnot(None)
        ).count()
        
        completed_deliveries = self.db.query(Order).filter(
            Order.status == OrderStatus.DELIVERED
        ).count()
        
        pending_deliveries = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED])
        ).count()
        
        return DeliveryStats(
            total_agents=total_agents,
            active_agents=active_agents,
            busy_agents=busy_agents,
            inactive_agents=inactive_agents,
            total_deliveries=total_deliveries,
            completed_deliveries=completed_deliveries,
            pending_deliveries=pending_deliveries
        )
