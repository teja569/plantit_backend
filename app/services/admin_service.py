from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
from app.models import User, Plant, Order, OrderItem, Prediction, DeliveryAgent, UserRole, OrderStatus, ApprovalStatus, Announcement
from app.schemas.admin import (
    DashboardStats, UserStats, PlantStats, OrderStats, RevenueStats,
    TopSeller, AdminDashboard, SystemHealth
)
from app.core.logging import logger
from io import BytesIO

# Optional reportlab import for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available - PDF generation will be disabled")


class AdminService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> DashboardStats:
        """Get overall dashboard statistics"""
        total_users = self.db.query(User).count()
        total_sellers = self.db.query(User).filter(User.role == UserRole.SELLER).count()
        total_plants = self.db.query(Plant).filter(Plant.is_active == True).count()
        total_orders = self.db.query(Order).count()
        
        total_revenue = self.db.query(Order).filter(
            Order.status == OrderStatus.DELIVERED
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        active_delivery_agents = self.db.query(DeliveryAgent).filter(
            DeliveryAgent.active_status == "active"
        ).count()
        
        pending_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING
        ).count()
        
        verified_plants = self.db.query(Plant).filter(
            Plant.verified_by_ai == True
        ).count()
        
        return DashboardStats(
            total_users=total_users,
            total_sellers=total_sellers,
            total_plants=total_plants,
            total_orders=total_orders,
            total_revenue=total_revenue,
            active_delivery_agents=active_delivery_agents,
            pending_orders=pending_orders,
            verified_plants=verified_plants
        )
    
    def get_user_stats(self) -> UserStats:
        """Get user statistics"""
        total_users = self.db.query(User).count()
        
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        new_users_today = self.db.query(User).filter(
            func.date(User.created_at) == today
        ).count()
        
        new_users_this_week = self.db.query(User).filter(
            User.created_at >= week_ago
        ).count()
        
        new_users_this_month = self.db.query(User).filter(
            User.created_at >= month_ago
        ).count()
        
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        return UserStats(
            total_users=total_users,
            new_users_today=new_users_today,
            new_users_this_week=new_users_this_week,
            new_users_this_month=new_users_this_month,
            verified_users=verified_users,
            active_users=active_users
        )
    
    def get_plant_stats(self) -> PlantStats:
        """Get plant statistics"""
        total_plants = self.db.query(Plant).filter(Plant.is_active == True).count()
        verified_plants = self.db.query(Plant).filter(
            and_(Plant.is_active == True, Plant.verified_by_ai == True)
        ).count()
        unverified_plants = total_plants - verified_plants
        
        # Plants by category
        plants_by_category = {}
        category_data = self.db.query(
            Plant.category, func.count(Plant.id)
        ).filter(Plant.is_active == True).group_by(Plant.category).all()
        
        for category, count in category_data:
            plants_by_category[category or "Uncategorized"] = count
        
        # Top selling plants
        top_selling = self.db.query(
            Plant.id, Plant.name, func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).filter(Plant.is_active == True).group_by(
            Plant.id, Plant.name
        ).order_by(desc('total_sold')).limit(10).all()
        
        top_selling_plants = [
            {"id": plant.id, "name": plant.name, "total_sold": plant.total_sold}
            for plant in top_selling
        ]
        
        return PlantStats(
            total_plants=total_plants,
            verified_plants=verified_plants,
            unverified_plants=unverified_plants,
            plants_by_category=plants_by_category,
            top_selling_plants=top_selling_plants
        )
    
    def get_order_stats(self) -> OrderStats:
        """Get order statistics"""
        total_orders = self.db.query(Order).count()
        
        status_counts = {}
        for status in OrderStatus:
            count = self.db.query(Order).filter(Order.status == status).count()
            status_counts[status.value] = count
        
        total_revenue = self.db.query(Order).filter(
            Order.status == OrderStatus.DELIVERED
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Revenue by time periods
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        revenue_today = self.db.query(Order).filter(
            and_(
                Order.status == OrderStatus.DELIVERED,
                func.date(Order.created_at) == today
            )
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        revenue_this_week = self.db.query(Order).filter(
            and_(
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= week_ago
            )
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        revenue_this_month = self.db.query(Order).filter(
            and_(
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= month_ago
            )
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        return OrderStats(
            total_orders=total_orders,
            pending_orders=status_counts.get('pending', 0),
            confirmed_orders=status_counts.get('confirmed', 0),
            shipped_orders=status_counts.get('shipped', 0),
            delivered_orders=status_counts.get('delivered', 0),
            cancelled_orders=status_counts.get('cancelled', 0),
            total_revenue=total_revenue,
            revenue_today=revenue_today,
            revenue_this_week=revenue_this_week,
            revenue_this_month=revenue_this_month
        )
    
    def get_revenue_stats(self) -> RevenueStats:
        """Get revenue statistics"""
        total_revenue = self.db.query(Order).filter(
            Order.status == OrderStatus.DELIVERED
        ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
        
        # Revenue by month (last 12 months)
        revenue_by_month = []
        for i in range(12):
            month_start = date.today().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            monthly_revenue = self.db.query(Order).filter(
                and_(
                    Order.status == OrderStatus.DELIVERED,
                    Order.created_at >= month_start,
                    Order.created_at < month_end
                )
            ).with_entities(func.sum(Order.total_price)).scalar() or 0.0
            
            revenue_by_month.append({
                "month": month_start.strftime("%Y-%m"),
                "revenue": monthly_revenue
            })
        
        revenue_by_month.reverse()  # Show oldest to newest
        
        return RevenueStats(
            total_revenue=total_revenue,
            revenue_today=0.0,  # Will be calculated in order_stats
            revenue_this_week=0.0,  # Will be calculated in order_stats
            revenue_this_month=0.0,  # Will be calculated in order_stats
            revenue_by_month=revenue_by_month
        )
    
    def get_top_sellers(self, limit: int = 10) -> List[TopSeller]:
        """Get top sellers by revenue"""
        top_sellers = self.db.query(
            User.id, User.name, func.sum(Order.total_price).label('total_sales'),
            func.count(Order.id).label('total_orders')
        ).join(Order, User.id == Order.seller_id).filter(
            Order.status == OrderStatus.DELIVERED
        ).group_by(User.id, User.name).order_by(
            desc('total_sales')
        ).limit(limit).all()
        
        return [
            TopSeller(
                seller_id=seller.id,
                seller_name=seller.name,
                total_sales=seller.total_sales,
                total_orders=seller.total_orders,
                plants_sold=0  # Could be calculated separately if needed
            )
            for seller in top_sellers
        ]
    
    def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders"""
        recent_orders = self.db.query(Order).order_by(
            desc(Order.created_at)
        ).limit(limit).all()
        
        return [
            {
                "id": order.id,
                "buyer_name": order.buyer.name,
                "seller_name": order.seller.name,
                "total_price": order.total_price,
                "status": order.status.value,
                "created_at": order.created_at
            }
            for order in recent_orders
        ]
    
    def get_recent_plants(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent plants"""
        recent_plants = self.db.query(Plant).filter(
            Plant.is_active == True
        ).order_by(desc(Plant.created_at)).limit(limit).all()
        
        return [
            {
                "id": plant.id,
                "name": plant.name,
                "price": plant.price,
                "seller_name": plant.seller.name,
                "verified_by_ai": plant.verified_by_ai,
                "created_at": plant.created_at
            }
            for plant in recent_plants
        ]
    
    def get_system_health(self) -> SystemHealth:
        """Get system health status"""
        try:
            # Test database connection
            self.db.execute("SELECT 1")
            database_status = "healthy"
        except Exception:
            database_status = "unhealthy"
        
        # Check ML model
        try:
            from app.services.ml_service import plant_classifier
            ml_model_status = "healthy" if plant_classifier.model else "not_configured"
        except Exception:
            ml_model_status = "unhealthy"
        
        # Check storage (simplified)
        storage_status = "healthy"  # In production, check actual storage
        
        # Check Redis (simplified)
        redis_status = "healthy"  # In production, check actual Redis
        
        return SystemHealth(
            database_status=database_status,
            ml_model_status=ml_model_status,
            storage_status=storage_status,
            redis_status=redis_status,
            uptime="N/A"  # Would need to track server start time
        )
    
    def get_admin_dashboard(self) -> AdminDashboard:
        """Get complete admin dashboard data"""
        stats = self.get_dashboard_stats()
        user_stats = self.get_user_stats()
        plant_stats = self.get_plant_stats()
        order_stats = self.get_order_stats()
        revenue_stats = self.get_revenue_stats()
        top_sellers = self.get_top_sellers()
        recent_orders = self.get_recent_orders()
        recent_plants = self.get_recent_plants()
        
        return AdminDashboard(
            stats=stats,
            user_stats=user_stats,
            plant_stats=plant_stats,
            order_stats=order_stats,
            revenue_stats=revenue_stats,
            top_sellers=top_sellers,
            recent_orders=recent_orders,
            recent_plants=recent_plants
        )

    def generate_order_invoice_pdf(self, order_id: int) -> bytes:
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("PDF generation is not available - ReportLab is not installed")
        
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, f"Invoice #{order.id}")
        y -= 30
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Buyer: {order.buyer.name} (ID: {order.buyer_id})")
        y -= 20
        c.drawString(50, y, f"Seller: {order.seller.name} (ID: {order.seller_id})")
        y -= 20
        c.drawString(50, y, f"Shipping Address: {order.shipping_address}")
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Items")
        y -= 20
        c.setFont("Helvetica", 12)
        for item in order.order_items:
            c.drawString(60, y, f"{item.quantity} x {item.plant.name} @ {item.unit_price} = {item.quantity * item.unit_price}")
            y -= 18
            if y < 100:
                c.showPage()
                y = height - 50
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Total: {order.total_price}")
        c.showPage()
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def create_announcement(self, title: str, message: str, audience: str | None, created_by: int | None) -> Announcement:
        ann = Announcement(title=title, message=message, audience=audience, created_by=created_by)
        self.db.add(ann)
        self.db.commit()
        self.db.refresh(ann)
        return ann

    def list_announcements(self, active_only: bool = True):
        q = self.db.query(Announcement)
        if active_only:
            q = q.filter(Announcement.is_active == True)
        return q.order_by(Announcement.created_at.desc()).all()

    def deactivate_announcement(self, announcement_id: int) -> bool:
        ann = self.db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not ann:
            return False
        ann.is_active = False
        self.db.commit()
        return True

    def update_vendor_status(self, user_id: int, status: ApprovalStatus) -> bool:
        """Approve or reject a vendor account"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        user.vendor_status = status
        # If approved, ensure role is seller; if rejected, keep role but mark inactive seller flow
        if status == ApprovalStatus.APPROVED and user.role == UserRole.USER:
            user.role = UserRole.SELLER
        self.db.commit()
        return True

    def update_plant_status(self, plant_id: int, status: ApprovalStatus) -> bool:
        """Approve or reject a product"""
        plant = self.db.query(Plant).filter(Plant.id == plant_id).first()
        if not plant:
            return False
        plant.approval_status = status
        self.db.commit()
        return True
