from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = Field(None, description="User who performed the action")
    entity_type: str
    entity_id: Optional[int] = None
    action: str
    data_before: Optional[str] = None
    data_after: Optional[str] = None
    metadata: Optional[str] = Field(
        None,
        description="Optional metadata JSON",
        alias="metadata_json",
    )
    timestamp: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int


