from pydantic import BaseModel, conint
from typing import List, Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    plant_id: int
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    plant_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    average_rating: float
    total: int

