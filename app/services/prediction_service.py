from sqlalchemy.orm import Session
from typing import Optional
from fastapi import UploadFile
from PIL import Image
from app.models import Prediction
from app.schemas.ml import PredictionResponse
from app.services.ml_service import plant_classifier
from app.core.logging import logger
import io


class MLService:
    def __init__(self, db: Session):
        self.db = db
    
    def predict_from_file(self, file: UploadFile, user_id: Optional[int] = None) -> PredictionResponse:
        """Make prediction from uploaded file"""
        try:
            # Read image
            image_data = file.file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Make prediction
            result = plant_classifier.predict(image)
            
            # Save prediction to database
            prediction = Prediction(
                image_url="",  # Will be updated after image upload
                is_plant=result["is_plant"],
                plant_type=result["plant_type"],
                confidence=result["confidence"],
                uploaded_by=user_id
            )
            
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)
            
            return PredictionResponse(
                is_plant=result["is_plant"],
                plant_type=result["plant_type"],
                confidence=result["confidence"],
                prediction_id=prediction.id
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def predict_from_url(self, image_url: str, user_id: Optional[int] = None) -> PredictionResponse:
        """Make prediction from image URL"""
        try:
            # Download image (simplified - in production, use proper image download)
            response = requests.get(image_url)
            image = Image.open(io.BytesIO(response.content))
            
            # Make prediction
            result = plant_classifier.predict(image)
            
            # Save prediction to database
            prediction = Prediction(
                image_url=image_url,
                is_plant=result["is_plant"],
                plant_type=result["plant_type"],
                confidence=result["confidence"],
                uploaded_by=user_id
            )
            
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)
            
            return PredictionResponse(
                is_plant=result["is_plant"],
                plant_type=result["plant_type"],
                confidence=result["confidence"],
                prediction_id=prediction.id
            )
            
        except Exception as e:
            logger.error(f"Prediction from URL failed: {e}")
            raise
    
    def get_prediction_history(self, user_id: int, limit: int = 50) -> list[Prediction]:
        """Get user's prediction history"""
        return self.db.query(Prediction).filter(
            Prediction.uploaded_by == user_id
        ).order_by(Prediction.timestamp.desc()).limit(limit).all()
    
    def get_prediction_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Get prediction by ID"""
        return self.db.query(Prediction).filter(Prediction.id == prediction_id).first()
