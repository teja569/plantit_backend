from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_active_user, require_seller_or_admin, require_admin
from app.schemas.plant import PlantCreate, PlantResponse, PlantUpdate, PlantListResponse, PlantSearchParams
from app.schemas.ml import PredictionResponse, PredictionLog
from app.services.plant_service import PlantService
from app.services.prediction_service import MLService
from app.models import User

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    category: Optional[str] = Form(None),
    species: Optional[str] = Form(None),
    care_instructions: Optional[str] = Form(None),
    stock_quantity: int = Form(0),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new plant listing"""
    plant_service = PlantService(db)
    
    plant_data = PlantCreate(
        name=name,
        description=description,
        price=price,
        category=category,
        species=species,
        care_instructions=care_instructions,
        stock_quantity=stock_quantity
    )
    
    plant = plant_service.create_plant(plant_data, current_user.id, image)
    return plant


@router.get("/", response_model=PlantListResponse)
async def get_plants(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    verified_only: Optional[bool] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """Get plants with filtering and pagination"""
    plant_service = PlantService(db)
    
    search_params = PlantSearchParams(
        name=name,
        category=category,
        min_price=min_price,
        max_price=max_price,
        verified_only=verified_only,
        page=page,
        size=size
    )
    
    plants, total = plant_service.get_plants(search_params)
    pages = (total + size - 1) // size
    
    return PlantListResponse(
        plants=plants,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant_id: int,
    db: Session = Depends(get_db)
):
    """Get plant by ID"""
    plant_service = PlantService(db)
    plant = plant_service.get_plant_by_id(plant_id)
    
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    
    return plant


@router.put("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_id: int,
    plant_data: PlantUpdate,
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Update plant information"""
    plant_service = PlantService(db)
    plant = plant_service.update_plant(plant_id, plant_data, current_user.id)
    
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found or not authorized"
        )
    
    return plant


@router.delete("/{plant_id}")
async def delete_plant(
    plant_id: int,
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Delete plant (deactivate)"""
    plant_service = PlantService(db)
    success = plant_service.delete_plant(plant_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found or not authorized"
        )
    
    return {"message": "Plant deleted successfully"}


@router.get("/seller/my-plants", response_model=PlantListResponse)
async def get_my_plants(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_seller_or_admin),
    db: Session = Depends(get_db)
):
    """Get current seller's plants"""
    plant_service = PlantService(db)
    plants, total = plant_service.get_seller_plants(current_user.id, page, size)
    pages = (total + size - 1) // size
    
    return PlantListResponse(
        plants=plants,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


# ML Prediction endpoints
@router.post("/predict", response_model=PredictionResponse)
async def predict_plant(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Predict plant type from uploaded image"""
    ml_service = MLService(db)
    
    try:
        result = ml_service.predict_from_file(image, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/predictions/history", response_model=List[PredictionLog])
async def get_prediction_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's prediction history"""
    ml_service = MLService(db)
    predictions = ml_service.get_prediction_history(current_user.id, limit)
    return predictions


@router.put("/{plant_id}/verify")
async def verify_plant(
    plant_id: int,
    verified: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Verify plant AI classification (admin only)"""
    plant_service = PlantService(db)
    success = plant_service.update_plant_verification(plant_id, verified)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    
    return {"message": f"Plant verification updated to {verified}"}
