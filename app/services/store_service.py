from typing import List, Tuple
from math import radians, sin, cos, asin, sqrt

from sqlalchemy.orm import Session

from app.models import Store


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two lat/lng pairs."""
    # Earth radius in kilometers
    r = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


class StoreService:
    """Service for store operations (nearby search, etc.)."""

    def __init__(self, db: Session):
        self.db = db

    def get_nearby_stores(
        self,
        lat: float,
        lng: float,
        radius_km: float = 10.0,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Store], int]:
        """
        Return stores within radius_km of (lat, lng), sorted by distance.

        For simplicity and SQLite compatibility we:
        - load candidate stores from DB
        - compute Haversine distance in Python
        - filter + sort + paginate in memory
        """
        if page < 1:
            page = 1
        if size < 1:
            size = 20

        # Load all stores; for real production with many stores,
        # add a rough bounding box filter here.
        stores = self.db.query(Store).all()

        # Compute distances
        stores_with_distance = []
        for store in stores:
            distance = _haversine_km(lat, lng, store.latitude, store.longitude)
            if distance <= radius_km:
                # Attach distance dynamically
                setattr(store, "distance_km", distance)
                stores_with_distance.append(store)

        # Sort by distance
        stores_with_distance.sort(key=lambda s: getattr(s, "distance_km", 0.0))

        total = len(stores_with_distance)
        start = (page - 1) * size
        end = start + size
        paginated = stores_with_distance[start:end]

        return paginated, total

    def create_store(self, store_data) -> Store:
        """Create a new store"""
        # Default to 0,0 if coordinates not provided (not ideal, but allows form submission)
        # TODO: Frontend should add geocoding or map picker to get real coordinates
        latitude = store_data.latitude if store_data.latitude is not None else 0.0
        longitude = store_data.longitude if store_data.longitude is not None else 0.0
        
        store = Store(
            name=store_data.name,
            address=store_data.address,
            latitude=latitude,
            longitude=longitude,
            phone=store_data.phone,
            rating=store_data.rating,
            total_reviews=store_data.total_reviews,
            is_partner=store_data.is_partner,
        )
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def get_all_stores(
        self,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Store], int]:
        """Get all stores with pagination"""
        if page < 1:
            page = 1
        if size < 1:
            size = 20

        # Get total count
        total = self.db.query(Store).count()

        # Apply pagination
        offset = (page - 1) * size
        stores = self.db.query(Store).offset(offset).limit(size).all()

        return stores, total


