from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PredictionRequest(BaseModel):
    image_url: Optional[str] = None


class PredictionResponse(BaseModel):
    is_plant: bool
    plant_type: str
    confidence: float
    prediction_id: Optional[int] = None


class PredictionLog(BaseModel):
    id: int
    image_url: str
    is_plant: bool
    plant_type: str
    confidence: float
    uploaded_by: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
