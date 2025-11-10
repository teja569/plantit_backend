from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
from app.models import User, Plant, Order, OrderItem, OrderStatus
from app.schemas.seller import SellerDashboard, SellerStats, SellerEarnings
from app.core.logging import logger


class SellerService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_seller_dashboard(self, seller_id: int) -> SellerDashboard:
        """Get seller dashboard data"""
        # Plant statistics
        total_plants = self.db.query(Plant).filter(Plant.seller_id == seller_id).count()
        active_plants = self.db.query(Plant).filter(
            and_(Plant.seller_id == seller_id, Plant.is_active == True)
        ).count()
        
        # Order statistics
        total_orders = self.db.query(Order).filter(Order.seller_id == seller_id).count()
        pending_orders = self.db.query(Order).filter(
            and_(Order.seller_id == seller_id, Order.status == OrderStatus.PENDING)
        ).count()
        completed_orders = self.db.query(Order).filter(
            and_(Order.seller_id == seller_id, Order.status == OrderStatus.DELIVERED)
        ).count()
        
        # Revenue statistics
        total_revenue = self.db.query(Order).filter(
            and_(Order.seller_id == seller_id, Order.status == OrderStatus.DELIVERED)
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Monthly revenue
        month_start = date.today().replace(day=1)
        monthly_revenue = self.db.query(Order).filter(
            and_(
                Order.seller_id == seller_id,
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= month_start
            )
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Top selling plants
        top_selling = self.db.query(
            Plant.id, Plant.name, func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).filter(
            Plant.seller_id == seller_id
        ).group_by(Plant.id, Plant.name).order_by(
            desc('total_sold')
        ).limit(5).all()
        
        top_selling_plants = [
            {"id": plant.id, "name": plant.name, "total_sold": plant.total_sold}
            for plant in top_selling
        ]
        
        # Recent orders
        recent_orders = self.db.query(Order).filter(
            Order.seller_id == seller_id
        ).order_by(desc(Order.created_at)).limit(5).all()
        
        recent_orders_data = [
            {
                "id": order.id,
                "buyer_name": order.buyer.name,
                "total_price": order.total_price,
                "status": order.status.value,
                "created_at": order.created_at
            }
            for order in recent_orders
        ]
        
        return SellerDashboard(
            total_plants=total_plants,
            active_plants=active_plants,
            total_orders=total_orders,
            pending_orders=pending_orders,
            completed_orders=completed_orders,
            total_revenue=total_revenue,
            monthly_revenue=monthly_revenue,
            top_selling_plants=top_selling_plants,
            recent_orders=recent_orders_data
        )
    
    def get_seller_stats(self, seller_id: int) -> SellerStats:
        """Get seller statistics"""
        # Plant stats
        total_plants = self.db.query(Plant).filter(Plant.seller_id == seller_id).count()
        verified_plants = self.db.query(Plant).filter(
            and_(Plant.seller_id == seller_id, Plant.verified_by_ai == True)
        ).count()
        
        # Order stats
        total_orders = self.db.query(Order).filter(Order.seller_id == seller_id).count()
        completed_orders = self.db.query(Order).filter(
            and_(Order.seller_id == seller_id, Order.status == OrderStatus.DELIVERED)
        ).count()
        
        # Revenue stats
        total_revenue = self.db.query(Order).filter(
            and_(Order.seller_id == seller_id, Order.status == OrderStatus.DELIVERED)
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        average_order_value = total_revenue / completed_orders if completed_orders > 0 else 0.0
        
        # Conversion rate (completed orders / total orders)
        conversion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0.0
        
        return SellerStats(
            total_plants=total_plants,
            verified_plants=verified_plants,
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_order_value=average_order_value,
            conversion_rate=conversion_rate
        )
    
    def get_seller_earnings(self, seller_id: int) -> SellerEarnings:
        """Get seller earnings breakdown"""
        # Total earnings (completed orders)
        total_earnings = self.db.query(Order).filter(
            and_(Order.seller_id == seller_id, Order.status == OrderStatus.DELIVERED)
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Pending earnings (confirmed/shipped orders)
        pending_earnings = self.db.query(Order).filter(
            and_(
                Order.seller_id == seller_id,
                Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED])
            )
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Available earnings (can be withdrawn)
        available_earnings = total_earnings  # Simplified - in production, consider processing fees
        
        # Monthly earnings
        month_start = date.today().replace(day=1)
        monthly_earnings = self.db.query(Order).filter(
            and_(
                Order.seller_id == seller_id,
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= month_start
            )
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Earnings by month (last 12 months)
        earnings_by_month = []
        for i in range(12):
            month_start = date.today().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            monthly_earning = self.db.query(Order).filter(
                and_(
                    Order.seller_id == seller_id,
                    Order.status == OrderStatus.DELIVERED,
                    Order.created_at >= month_start,
                    Order.created_at < month_end
                )
            ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
            
            earnings_by_month.append({
                "month": month_start.strftime("%Y-%m"),
                "earnings": monthly_earning
            })
        
        earnings_by_month.reverse()  # Show oldest to newest
        
        return SellerEarnings(
            total_earnings=total_earnings,
            pending_earnings=pending_earnings,
            available_earnings=available_earnings,
            earnings_this_month=monthly_earnings,
            earnings_by_month=earnings_by_month
        )
    
    def update_seller_profile(self, seller_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update seller profile information"""
        seller = self.db.query(User).filter(User.id == seller_id).first()
        if not seller:
            return False
        
        # Update seller-specific fields
        for field, value in profile_data.items():
            if hasattr(seller, field):
                setattr(seller, field, value)
        
        self.db.commit()
        logger.info(f"Seller {seller_id} profile updated")
        return True
    
    def get_seller_performance(self, seller_id: int, days: int = 30) -> Dict[str, Any]:
        """Get seller performance metrics"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Orders in period
        orders_in_period = self.db.query(Order).filter(
            and_(
                Order.seller_id == seller_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).count()
        
        # Revenue in period
        revenue_in_period = self.db.query(Order).filter(
            and_(
                Order.seller_id == seller_id,
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Plants sold in period
        plants_sold = self.db.query(func.sum(OrderItem.quantity)).join(Order).filter(
            and_(
                Order.seller_id == seller_id,
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).scalar() or 0
        
        return {
            "period_days": days,
            "orders_count": orders_in_period,
            "revenue": revenue_in_period,
            "plants_sold": plants_sold,
            "average_order_value": revenue_in_period / orders_in_period if orders_in_period > 0 else 0
        }
