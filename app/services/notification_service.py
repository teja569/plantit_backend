from sqlalchemy.orm import Session
from app.models import DeviceToken, NotificationPreference


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def register_device_token(self, user_id: int, token: str, platform: str | None) -> None:
        existing = self.db.query(DeviceToken).filter(DeviceToken.token == token).first()
        if existing:
            existing.user_id = user_id
            existing.platform = platform
        else:
            self.db.add(DeviceToken(user_id=user_id, token=token, platform=platform))
        self.db.commit()

    def update_preferences(self, user_id: int, **prefs) -> NotificationPreference:
        pref = self.db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.db.add(pref)
        for k, v in prefs.items():
            if v is not None and hasattr(pref, k):
                setattr(pref, k, v)
        self.db.commit()
        self.db.refresh(pref)
        return pref


