from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.core.security import require_seller_or_admin, get_current_active_user
from app.schemas.seller import SellerDashboard, SellerStats, SellerEarnings, SellerOnboarding, SellerProfile
from app.services.seller_service import SellerService
from app.models import User, ApprovalStatus

router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("/onboard")
async def seller_onboarding(
    onboarding_data: SellerOnboarding,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Complete seller onboarding process"""
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only regular users can become sellers"
        )
    
    seller_service = SellerService(db)
    
    # Mark vendor status as pending approval; role will be set on approval
    current_user.vendor_status = ApprovalStatus.PENDING
    
    # Update profile with business information
    profile_data = onboarding_data.dict()
    success = seller_service.update_seller_profile(current_user.id, profile_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update seller profile"
        )
    
    db.commit()
    
    return {"message": "Seller onboarding completed successfully"}


@router.get("/dashboard", response_model=SellerDashboard)
async def get_seller_dashboard(
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Get seller dashboard data"""
    seller_service = SellerService(db)
    dashboard = seller_service.get_seller_dashboard(current_user.id)
    return dashboard


@router.get("/stats", response_model=SellerStats)
async def get_seller_stats(
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Get seller statistics"""
    seller_service = SellerService(db)
    stats = seller_service.get_seller_stats(current_user.id)
    return stats


@router.get("/earnings", response_model=SellerEarnings)
async def get_seller_earnings(
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Get seller earnings breakdown"""
    seller_service = SellerService(db)
    earnings = seller_service.get_seller_earnings(current_user.id)
    return earnings


@router.get("/performance")
async def get_seller_performance(
    days: int = 30,
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Get seller performance metrics"""
    seller_service = SellerService(db)
    performance = seller_service.get_seller_performance(current_user.id, days)
    return performance


@router.put("/profile", response_model=SellerProfile)
async def update_seller_profile(
    profile_data: SellerProfile,
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Update seller profile information"""
    seller_service = SellerService(db)
    
    update_data = profile_data.dict(exclude_unset=True)
    success = seller_service.update_seller_profile(current_user.id, update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update seller profile"
        )
    
    # Return updated profile
    updated_user = db.query(User).filter(User.id == current_user.id).first()
    return SellerProfile(
        business_name=getattr(updated_user, 'business_name', None),
        business_type=getattr(updated_user, 'business_type', None),
        tax_id=getattr(updated_user, 'tax_id', None),
        business_address=getattr(updated_user, 'business_address', None),
        business_phone=getattr(updated_user, 'business_phone', None),
        business_email=getattr(updated_user, 'business_email', None),
        description=getattr(updated_user, 'description', None),
        is_verified=updated_user.is_verified
    )


@router.get("/profile", response_model=SellerProfile)
async def get_seller_profile(
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Get seller profile information"""
    return SellerProfile(
        business_name=getattr(current_user, 'business_name', None),
        business_type=getattr(current_user, 'business_type', None),
        tax_id=getattr(current_user, 'tax_id', None),
        business_address=getattr(current_user, 'business_address', None),
        business_phone=getattr(current_user, 'business_phone', None),
        business_email=getattr(current_user, 'business_email', None),
        description=getattr(current_user, 'description', None),
        is_verified=current_user.is_verified
    )
