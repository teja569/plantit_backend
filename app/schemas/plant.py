from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PlantBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    species: Optional[str] = None
    care_instructions: Optional[str] = None
    stock_quantity: int = 0


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    species: Optional[str] = None
    care_instructions: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class PlantResponse(PlantBase):
    id: int
    image_url: Optional[str] = None
    seller_id: int
    verified_by_ai: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PlantListResponse(BaseModel):
    plants: List[PlantResponse]
    total: int
    page: int
    size: int
    pages: int


class PlantSearchParams(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    verified_only: Optional[bool] = None
    page: int = 1
    size: int = 20
