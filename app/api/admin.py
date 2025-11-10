from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.admin import AdminDashboard, SystemHealth, UserStats, PlantStats, OrderStats, RevenueStats, TopSeller, AnnouncementCreate, AnnouncementResponse
from app.services.admin_service import AdminService
from app.models import User, ApprovalStatus
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboard)
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get complete admin dashboard data"""
    admin_service = AdminService(db)
    dashboard = admin_service.get_admin_dashboard()
    return dashboard


@router.get("/stats/users", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    admin_service = AdminService(db)
    stats = admin_service.get_user_stats()
    return stats


@router.get("/stats/plants", response_model=PlantStats)
async def get_plant_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get plant statistics"""
    admin_service = AdminService(db)
    stats = admin_service.get_plant_stats()
    return stats


@router.get("/stats/orders", response_model=OrderStats)
async def get_order_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get order statistics"""
    admin_service = AdminService(db)
    stats = admin_service.get_order_stats()
    return stats


@router.get("/stats/revenue", response_model=RevenueStats)
async def get_revenue_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get revenue statistics"""
    admin_service = AdminService(db)
    stats = admin_service.get_revenue_stats()
    return stats


@router.get("/top-sellers", response_model=List[TopSeller])
async def get_top_sellers(
    limit: int = 10,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get top sellers by revenue"""
    admin_service = AdminService(db)
    sellers = admin_service.get_top_sellers(limit)
    return sellers


@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    admin_service = AdminService(db)
    health = admin_service.get_system_health()
    return health


@router.get("/recent-orders")
async def get_recent_orders(
    limit: int = 10,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get recent orders"""
    admin_service = AdminService(db)
    orders = admin_service.get_recent_orders(limit)
    return {"recent_orders": orders}


@router.get("/recent-plants")
async def get_recent_plants(
    limit: int = 10,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get recent plants"""
    admin_service = AdminService(db)
    plants = admin_service.get_recent_plants(limit)
    return {"recent_plants": plants}


@router.put("/vendors/{user_id}/status")
async def update_vendor_status(
    user_id: int,
    status: ApprovalStatus,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve or reject vendor (admin or higher)"""
    admin_service = AdminService(db)
    success = admin_service.update_vendor_status(user_id, status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"Vendor status updated to {status.value}"}


@router.put("/plants/{plant_id}/status")
async def update_plant_approval(
    plant_id: int,
    status: ApprovalStatus,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve or reject product (admin or higher)"""
    admin_service = AdminService(db)
    success = admin_service.update_plant_status(plant_id, status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    return {"message": f"Plant status updated to {status.value}"}


@router.get("/orders/{order_id}/invoice.pdf")
async def download_invoice(
    order_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Generate and download invoice PDF for an order (admin/manager)."""
    admin_service = AdminService(db)
    try:
        pdf_bytes = admin_service.generate_order_invoice_pdf(order_id)
        return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=invoice_{order_id}.pdf"
        })
    except ValueError:
        raise HTTPException(status_code=404, detail="Order not found")


@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    body: AnnouncementCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    admin_service = AdminService(db)
    ann = admin_service.create_announcement(body.title, body.message, body.audience, current_user.id)
    return ann


@router.get("/announcements", response_model=List[AnnouncementResponse])
async def list_announcements(
    active_only: bool = True,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    admin_service = AdminService(db)
    anns = admin_service.list_announcements(active_only)
    return anns


@router.delete("/announcements/{announcement_id}")
async def deactivate_announcement(
    announcement_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    admin_service = AdminService(db)
    ok = admin_service.deactivate_announcement(announcement_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deactivated"}
