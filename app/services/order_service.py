from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from app.models import Order, OrderItem, Plant, User, OrderStatus, Cart, CartItem, DeliveryTimeline
from app.schemas.order import OrderCreate, OrderUpdate, OrderStats, CheckoutRequest
from app.core.logging import logger


class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_order(self, order_data: OrderCreate, buyer_id: int) -> Order:
        """Create a new order"""
        try:
            # Validate plants and calculate total
            total_price = 0.0
            order_items = []
            
            for item in order_data.items:
                plant = self.db.query(Plant).filter(
                    and_(Plant.id == item.plant_id, Plant.is_active == True)
                ).first()
                
                if not plant:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Plant with ID {item.plant_id} not found"
                    )
                
                if plant.stock_quantity < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for plant {plant.name}"
                    )
                
                item_total = plant.price * item.quantity
                total_price += item_total
                
                order_items.append({
                    'plant_id': item.plant_id,
                    'quantity': item.quantity,
                    'unit_price': plant.price
                })
            
            # Create order
            db_order = Order(
                buyer_id=buyer_id,
                seller_id=order_data.seller_id,
                status=OrderStatus.PENDING,
                total_price=total_price,
                shipping_address=order_data.shipping_address,
                notes=order_data.notes
            )
            
            self.db.add(db_order)
            self.db.flush()  # Get the order ID
            
            # Create order items
            for item_data in order_items:
                order_item = OrderItem(
                    order_id=db_order.id,
                    plant_id=item_data['plant_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
                self.db.add(order_item)
                
                # Update plant stock
                plant = self.db.query(Plant).filter(Plant.id == item_data['plant_id']).first()
                plant.stock_quantity -= item_data['quantity']
            
            self.db.commit()
            self.db.refresh(db_order)
            
            logger.info(f"Order {db_order.id} created successfully")
            return db_order
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create order: {e}")
            raise
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_user_orders(self, user_id: int, page: int = 1, size: int = 20) -> Tuple[List[Order], int]:
        """Get orders for a user (as buyer)"""
        query = self.db.query(Order).filter(Order.buyer_id == user_id)
        total = query.count()
        
        offset = (page - 1) * size
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(size).all()
        
        return orders, total
    
    def get_seller_orders(self, seller_id: int, page: int = 1, size: int = 20) -> Tuple[List[Order], int]:
        """Get orders for a seller"""
        query = self.db.query(Order).filter(Order.seller_id == seller_id)
        total = query.count()
        
        offset = (page - 1) * size
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(size).all()
        
        return orders, total
    
    def update_order_status(self, order_id: int, status: OrderStatus, user_id: int) -> Optional[Order]:
        """Update order status"""
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        
        # Check permissions
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order"
            )
        
        order.status = status
        # Append to delivery timeline
        try:
            self.db.add(DeliveryTimeline(order_id=order.id, status=status.value, note=None))
        except Exception:
            pass
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Order {order_id} status updated to {status}")
        return order
    
    def assign_delivery_agent(self, order_id: int, delivery_agent_id: int) -> Optional[Order]:
        """Assign delivery agent to order"""
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        
        order.delivery_agent_id = delivery_agent_id
        order.status = OrderStatus.CONFIRMED
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Delivery agent {delivery_agent_id} assigned to order {order_id}")
        return order
    
    def cancel_order(self, order_id: int, user_id: int) -> bool:
        """Cancel an order and restore stock"""
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        
        # Check permissions
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this order"
            )
        
        # Only allow cancellation if order is pending or confirmed
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel order in current status"
            )
        
        # Restore stock
        for item in order.order_items:
            plant = self.db.query(Plant).filter(Plant.id == item.plant_id).first()
            if plant:
                plant.stock_quantity += item.quantity
        
        order.status = OrderStatus.CANCELLED
        self.db.commit()
        
        logger.info(f"Order {order_id} cancelled and stock restored")
        return True
    
    def get_order_stats(self, user_id: int, user_role: str) -> OrderStats:
        """Get order statistics for user"""
        if user_role == "seller":
            query = self.db.query(Order).filter(Order.seller_id == user_id)
        else:
            query = self.db.query(Order).filter(Order.buyer_id == user_id)
        
        total_orders = query.count()
        pending_orders = query.filter(Order.status == OrderStatus.PENDING).count()
        completed_orders = query.filter(Order.status == OrderStatus.DELIVERED).count()
        cancelled_orders = query.filter(Order.status == OrderStatus.CANCELLED).count()
        
        total_revenue = query.filter(Order.status == OrderStatus.DELIVERED).with_entities(
            func.sum(Order.total_price)
        ).scalar() or 0.0
        
        return OrderStats(
            total_orders=total_orders,
            pending_orders=pending_orders,
            completed_orders=completed_orders,
            cancelled_orders=cancelled_orders,
            total_revenue=total_revenue
        )

    def checkout_from_cart(self, buyer_id: int, body: CheckoutRequest):
        """Convert cart into orders grouped by seller. Returns list of created orders."""
        cart = self.db.query(Cart).filter(Cart.user_id == buyer_id).first()
        if not cart or not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        # Group items by seller
        items_by_seller = {}
        for item in cart.items:
            plant = self.db.query(Plant).filter(Plant.id == item.plant_id).first()
            if not plant or plant.stock_quantity < item.quantity or not plant.is_active:
                raise HTTPException(status_code=400, detail=f"Item unavailable: {item.plant_id}")
            items_by_seller.setdefault(plant.seller_id, []).append((plant, item))

        created_orders = []
        try:
            for seller_id, pairs in items_by_seller.items():
                total_price = sum(p.price * it.quantity for p, it in pairs)
                order = Order(
                    buyer_id=buyer_id,
                    seller_id=seller_id,
                    status=OrderStatus.PENDING,
                    total_price=total_price,
                    shipping_address=body.shipping_address,
                    notes=body.notes,
                )
                self.db.add(order)
                self.db.flush()
                for plant, it in pairs:
                    self.db.add(OrderItem(order_id=order.id, plant_id=plant.id, quantity=it.quantity, unit_price=plant.price))
                    plant.stock_quantity -= it.quantity
                created_orders.append(order)

            # Clear cart
            for ci in list(cart.items):
                self.db.delete(ci)
            self.db.commit()
            for o in created_orders:
                self.db.refresh(o)
            return created_orders
        except Exception as e:
            self.db.rollback()
            raise
