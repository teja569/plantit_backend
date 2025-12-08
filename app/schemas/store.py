from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StoreBase(BaseModel):
    name: str = Field(..., description="Store name")
    address: str = Field(..., description="Full address of the store")
    latitude: Optional[float] = Field(None, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, description="Longitude in decimal degrees")
    phone: Optional[str] = Field(None, description="Contact phone number")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating 0-5")
    total_reviews: Optional[int] = Field(None, ge=0, description="Total number of reviews")
    is_partner: bool = Field(False, description="Whether this store is a PlantIt partner")


class StoreCreate(StoreBase):
    """Schema for creating a new store"""
    pass


class StoreResponse(StoreBase):
    id: int
    created_at: datetime
    distance_km: Optional[float] = Field(
        None,
        description="Distance from the user in kilometers (only for nearby queries)",
    )

    class Config:
        from_attributes = True


class StoreListResponse(BaseModel):
    stores: List[StoreResponse]
    total: int
    page: int
    size: int
    pages: int


class NearbyStoresResponse(BaseModel):
    stores: List[StoreResponse]
    total: int
    page: int
    size: int
    pages: int


