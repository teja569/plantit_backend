from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Tuple, List
from app.models import Review, Plant


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create_review(self, user_id: int, plant_id: int, rating: int, comment: str | None) -> Review:
        plant = self.db.query(Plant).filter(Plant.id == plant_id, Plant.is_active == True).first()
        if not plant:
            raise ValueError("Plant not found")
        review = Review(user_id=user_id, plant_id=plant_id, rating=rating, comment=comment)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_reviews_for_plant(self, plant_id: int) -> Tuple[List[Review], float, int]:
        reviews = self.db.query(Review).filter(Review.plant_id == plant_id).order_by(Review.created_at.desc()).all()
        total = len(reviews)
        avg = self.db.query(func.avg(Review.rating)).filter(Review.plant_id == plant_id).scalar() or 0.0
        return reviews, float(avg), total


