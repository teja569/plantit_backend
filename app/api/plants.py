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
    category: str = Form(...),  # Required field
    price: str = Form(...),  # Receive as string, convert to float
    stock: Optional[str] = Form(None),  # Accept 'stock' field
    stock_quantity: Optional[str] = Form(None),  # Also accept 'stock_quantity' for compatibility
    description: Optional[str] = Form(None),
    verified: Optional[str] = Form(None),  # Accept 'verified' field
    verified_by_ai: Optional[str] = Form(None),  # Also accept 'verified_by_ai' for compatibility
    image: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),  # Alternative to file upload
    species: Optional[str] = Form(None),
    care_instructions: Optional[str] = Form(None),
    current_user: User = Depends(require_admin),  # Admin only as per frontend requirements
    db: Session = Depends(get_db)
):
    """
    Create a new plant listing (admin only).
    
    Required fields:
    - name: Plant name
    - category: Plant category (e.g., "Indoor", "Outdoor")
    - price: Plant price (as string, will be converted to float)
    - stock: Stock quantity (as string, will be converted to int)
    
    Optional fields:
    - description: Plant description
    - verified: Verification status ("true" or "false", default: "false")
    - image: Image file upload (requires S3 configuration)
    - image_url: Image URL (alternative to file upload)
    - species: Plant species
    - care_instructions: Care instructions
    """
    plant_service = PlantService(db)
    
    # Determine stock value: prefer 'stock', fallback to 'stock_quantity'
    stock_value = stock or stock_quantity
    if not stock_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'stock' or 'stock_quantity' field is required"
        )
    
    # Determine verified value: prefer 'verified', fallback to 'verified_by_ai'
    verified_value = verified or verified_by_ai or "false"
    
    # Convert string inputs to proper types
    try:
        price_float = float(price)
        if price_float <= 0:
            raise ValueError("Price must be greater than 0")
        stock_int = int(stock_value)
        if stock_int < 0:
            raise ValueError("Stock must be non-negative")
        verified_bool = verified_value.lower() == "true" if verified_value else False
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input format: {str(e)}"
        )
    
    # Handle image: prefer image_url if provided, otherwise upload file
    final_image_url = image_url
    
    if image and not final_image_url:
        # Upload image file to S3
        try:
            final_image_url = plant_service.upload_image_to_s3(image)
        except HTTPException:
            # Re-raise HTTP exceptions (already formatted)
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )
    
    # Create plant data
    plant_data = PlantCreate(
        name=name,
        description=description,
        price=price_float,
        category=category,
        species=species,
        care_instructions=care_instructions,
        stock_quantity=stock_int  # Map 'stock' to 'stock_quantity' internally
    )
    
    # Create plant with image_url and verified status
    plant = plant_service.create_plant(
        plant_data, 
        current_user.id, 
        image_file=None if final_image_url else image,  # Only pass file if no URL
        image_url=final_image_url,
        verified_by_ai=verified_bool
    )
    
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
