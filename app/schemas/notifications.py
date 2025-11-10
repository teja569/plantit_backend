from pydantic import BaseModel


class DeviceTokenRegister(BaseModel):
    token: str
    platform: str | None = None


class NotificationPreferenceUpdate(BaseModel):
    push_enabled: bool | None = None
    email_enabled: bool | None = None
    sms_enabled: bool | None = None


