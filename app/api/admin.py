from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.admin import AdminDashboard, SystemHealth, UserStats, PlantStats, OrderStats, RevenueStats, TopSeller, AnnouncementCreate, AnnouncementResponse
from app.schemas.audit import AuditLogResponse, AuditLogListResponse
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.schemas.store import StoreListResponse
from app.services.admin_service import AdminService
from app.services.audit_service import AuditService
from app.services.user_service import UserService
from app.services.store_service import StoreService
from app.models import User, ApprovalStatus, AuditLog, AuditAction
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


# ---------------------------------------------------------------------------
# Admin User Management
# ---------------------------------------------------------------------------

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    body: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new user (any role) from the admin panel."""
    user_service = UserService(db)
    audit = AuditService(db)

    user = user_service.create_user(body)
    after = UserResponse.model_validate(user).model_dump()

    audit.log(
        user_id=current_user.id,
        entity_type="user",
        entity_id=user.id,
        action=AuditAction.CREATE,
        data_before=None,
        data_after=after,
    )

    return UserResponse.model_validate(user)

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List users for admin management with basic filters."""
    query = db.query(User)

    if search:
        like = f"%{search}%"
        query = query.filter((User.name.ilike(like)) | (User.email.ilike(like)))
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)

    total = query.count()
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return [UserResponse.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get single user details for admin."""
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    body: UserUpdate,
    role: Optional[str] = Query(None, description="New role for the user"),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Update user fields as admin.

    - Can change profile fields via body
    - Can change role, is_active, is_verified via query params
    """
    user_service = UserService(db)
    audit = AuditService(db)

    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    before = UserResponse.model_validate(user).model_dump()

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    if is_verified is not None:
        user.is_verified = is_verified

    db.commit()
    db.refresh(user)

    after = UserResponse.model_validate(user).model_dump()

    action = AuditAction.ROLE_CHANGE if role is not None else AuditAction.UPDATE
    audit.log(
        user_id=current_user.id,
        entity_type="user",
        entity_id=user.id,
        action=action,
        data_before=before,
        data_after=after,
    )

    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------

@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    from_ts: Optional[str] = Query(None, alias="from"),
    to_ts: Optional[str] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Paginated audit log listing for admins."""
    query = db.query(AuditLog)

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if from_ts:
        query = query.filter(AuditLog.timestamp >= from_ts)
    if to_ts:
        query = query.filter(AuditLog.timestamp <= to_ts)

    total = query.count()
    logs = (
        query.order_by(AuditLog.timestamp.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    pages = (total + size - 1) // size
    items = [AuditLogResponse.model_validate(log) for log in logs]

    return AuditLogListResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log_detail(
    log_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get single audit log entry."""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return AuditLogResponse.model_validate(log)


@router.get("/stores", response_model=StoreListResponse)
async def get_admin_stores(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get all stores with pagination (admin only)"""
    try:
        service = StoreService(db)
        stores, total = service.get_all_stores(page=page, size=size)
        pages = (total + size - 1) // size

        from app.schemas.store import StoreResponse
        response_stores = [StoreResponse.from_orm(store) for store in stores]

        return StoreListResponse(
            stores=response_stores,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stores: {str(e)}"
        )
