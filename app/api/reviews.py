from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewListResponse
from app.services.review_service import ReviewService
from app.models import User


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse)
async def create_review(
    body: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    svc = ReviewService(db)
    try:
        review = svc.create_review(current_user.id, body.plant_id, body.rating, body.comment)
        return review
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/plant/{plant_id}", response_model=ReviewListResponse)
async def get_reviews(
    plant_id: int,
    db: Session = Depends(get_db)
):
    svc = ReviewService(db)
    reviews, avg, total = svc.get_reviews_for_plant(plant_id)
    return ReviewListResponse(reviews=reviews, average_rating=avg, total=total)


