from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.notifications import DeviceTokenRegister, NotificationPreferenceUpdate
from app.services.notification_service import NotificationService
from app.models import User


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/register-token")
async def register_token(
    body: DeviceTokenRegister,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    svc = NotificationService(db)
    svc.register_device_token(current_user.id, body.token, body.platform)
    return {"message": "registered"}


@router.put("/preferences")
async def update_preferences(
    body: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    svc = NotificationService(db)
    pref = svc.update_preferences(current_user.id, **body.dict())
    return {
        "push_enabled": pref.push_enabled,
        "email_enabled": pref.email_enabled,
        "sms_enabled": pref.sms_enabled,
    }


