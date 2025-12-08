from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.store import StoreResponse, NearbyStoresResponse, StoreCreate, StoreListResponse
from app.services.store_service import StoreService
from app.models import User


router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("/", response_model=StoreListResponse)
async def get_stores(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get all stores with pagination (admin only)"""
    try:
        service = StoreService(db)
        stores, total = service.get_all_stores(page=page, size=size)
        pages = (total + size - 1) // size

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


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    store_data: StoreCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new store (admin only)"""
    try:
        service = StoreService(db)
        store = service.create_store(store_data)
        return store
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create store: {str(e)}"
        )


@router.get("/nearby", response_model=NearbyStoresResponse)
async def get_nearby_stores(
    lat: float = Query(..., description="User latitude in decimal degrees"),
    lng: float = Query(..., description="User longitude in decimal degrees"),
    radius_km: float = Query(10.0, gt=0, description="Search radius in kilometers"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get nearby plant stores for the given location.

    The response includes distance (in km) from the given coordinates.
    """
    try:
        service = StoreService(db)
        stores, total = service.get_nearby_stores(
            lat=lat, lng=lng, radius_km=radius_km, page=page, size=size
        )
        pages = (total + size - 1) // size

        # Convert to response models and ensure distance_km is included
        response_stores = []
        for store in stores:
            data = StoreResponse.from_orm(store)
            # distance_km is attached dynamically in the service
            distance = getattr(store, "distance_km", None)
            if distance is not None:
                data.distance_km = distance
            response_stores.append(data)

        return NearbyStoresResponse(
            stores=response_stores,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
    except Exception as e:
        # Let global exception handler log details; return generic error
        raise HTTPException(status_code=500, detail="Failed to fetch nearby stores")


