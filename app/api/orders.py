from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user, require_seller_or_admin, require_admin
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate, OrderListResponse, OrderStats, CheckoutRequest, CheckoutResponse, CheckoutOrderSummary
from app.services.order_service import OrderService
from app.models import User, OrderStatus, UserRole, DeliveryTimeline

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    order_service = OrderService(db)
    order = order_service.create_order(order_data, current_user.id)
    return order


@router.get("/", response_model=OrderListResponse)
async def get_my_orders(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders"""
    order_service = OrderService(db)
    orders, total = order_service.get_user_orders(current_user.id, page, size)
    pages = (total + size - 1) // size
    
    return OrderListResponse(
        orders=orders,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/seller", response_model=OrderListResponse)
async def get_seller_orders(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Get seller's orders"""
    order_service = OrderService(db)
    orders, total = order_service.get_seller_orders(current_user.id, page, size)
    pages = (total + size - 1) // size
    
    return OrderListResponse(
        orders=orders,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    order_service = OrderService(db)
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if (
        order.buyer_id != current_user.id
        and order.seller_id != current_user.id
        and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update order status"""
    order_service = OrderService(db)
    order = order_service.update_order_status(order_id, status, current_user.id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.put("/{order_id}/assign-delivery")
async def assign_delivery_agent(
    order_id: int,
    delivery_agent_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign delivery agent to order (admin only)"""
    order_service = OrderService(db)
    order = order_service.assign_delivery_agent(order_id, delivery_agent_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return {"message": "Delivery agent assigned successfully"}


@router.put("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an order"""
    order_service = OrderService(db)
    success = order_service.cancel_order(order_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return {"message": "Order cancelled successfully"}


@router.get("/stats/my-stats", response_model=OrderStats)
async def get_my_order_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's order statistics"""
    order_service = OrderService(db)
    stats = order_service.get_order_stats(current_user.id, current_user.role)
    return stats


@router.get("/{order_id}/timeline")
async def get_order_timeline(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    order_service = OrderService(db)
    order = order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if (
        order.buyer_id != current_user.id
        and order.seller_id != current_user.id
        and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    items = db.query(DeliveryTimeline).filter(DeliveryTimeline.order_id == order_id).order_by(DeliveryTimeline.timestamp.asc()).all()
    return {
        "timeline": [
            {
                "status": t.status,
                "note": t.note,
                "timestamp": t.timestamp,
            }
            for t in items
        ]
    }


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Checkout the current user's cart and create orders grouped by seller.
    Payment handling will be performed in the payments phase. For COD, no payment payload is required."""
    order_service = OrderService(db)
    orders = order_service.checkout_from_cart(current_user.id, body)
    summaries = [
        CheckoutOrderSummary(order_id=o.id, seller_id=o.seller_id, total_price=o.total_price, status=o.status)
        for o in orders
    ]
    if body.payment_method == "cod":
        return CheckoutResponse(orders=summaries, payment_required=False)
    else:
        # Placeholder; Razorpay payload will be added in payments phase
        return CheckoutResponse(orders=summaries, payment_required=True, payment_provider="razorpay", payment_payload={})
