import os
import uuid
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import Plant, User, ApprovalStatus, UserRole
from app.schemas.plant import PlantCreate, PlantUpdate, PlantSearchParams
from app.core.config import settings
from PIL import Image
import io

# Optional boto3 import for S3 storage
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception


class PlantService:
    def __init__(self, db: Session):
        self.db = db
        self.s3_client = None
        if BOTO3_AVAILABLE and settings.aws_access_key_id and settings.aws_secret_access_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
            except Exception:
                self.s3_client = None
    
    def upload_image_to_s3(self, file: UploadFile) -> str:
        """Upload image to S3 and return URL"""
        if not self.s3_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3 configuration not available"
            )
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Process image
        try:
            image = Image.open(file.file)
            # Resize if too large
            if image.size[0] > 1920 or image.size[1] > 1920:
                image.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
            filename = f"plants/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                img_buffer,
                settings.aws_bucket_name,
                filename,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            
            # Return public URL
            return f"https://{settings.aws_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{filename}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )
    
    def create_plant(self, plant_data: PlantCreate, seller_id: int, image_file: Optional[UploadFile] = None, image_url: Optional[str] = None, verified_by_ai: Optional[bool] = None) -> Plant:
        """Create a new plant listing"""
        # Ensure seller is approved or is admin
        seller = self.db.query(User).filter(User.id == seller_id).first()
        if not seller:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
        if seller.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER] and getattr(seller, 'vendor_status', None) != ApprovalStatus.APPROVED:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor not approved")
        
        # Auto-approve plants created by admins/managers
        is_admin = seller.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER]
        approval_status = ApprovalStatus.APPROVED if is_admin else ApprovalStatus.PENDING
        
        # Handle image: prefer provided image_url, otherwise upload file
        final_image_url = image_url
        if image_file and not final_image_url:
            final_image_url = self.upload_image_to_s3(image_file)
        
        db_plant = Plant(
            name=plant_data.name,
            description=plant_data.description,
            image_url=final_image_url,
            price=plant_data.price,
            category=plant_data.category,
            species=plant_data.species,
            care_instructions=plant_data.care_instructions,
            stock_quantity=plant_data.stock_quantity,
            seller_id=seller_id,
            verified_by_ai=verified_by_ai if verified_by_ai is not None else False,
            approval_status=approval_status
        )
        
        self.db.add(db_plant)
        self.db.commit()
        self.db.refresh(db_plant)
        return db_plant
    
    def get_plant_by_id(self, plant_id: int) -> Optional[Plant]:
        """Get plant by ID"""
        return self.db.query(Plant).filter(Plant.id == plant_id).first()
    
    def get_plants(self, search_params: PlantSearchParams) -> tuple[List[Plant], int]:
        """Get plants with filtering and pagination"""
        query = self.db.query(Plant).filter(Plant.is_active == True, Plant.approval_status == ApprovalStatus.APPROVED)
        
        # Apply filters
        if search_params.name:
            query = query.filter(Plant.name.ilike(f"%{search_params.name}%"))
        
        if search_params.category:
            query = query.filter(Plant.category == search_params.category)
        
        if search_params.min_price is not None:
            query = query.filter(Plant.price >= search_params.min_price)
        
        if search_params.max_price is not None:
            query = query.filter(Plant.price <= search_params.max_price)
        
        if search_params.verified_only:
            query = query.filter(Plant.verified_by_ai == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.size
        plants = query.offset(offset).limit(search_params.size).all()
        
        return plants, total
    
    def update_plant(self, plant_id: int, plant_data: PlantUpdate, seller_id: int) -> Optional[Plant]:
        """Update plant information"""
        plant = self.db.query(Plant).filter(
            and_(Plant.id == plant_id, Plant.seller_id == seller_id)
        ).first()
        
        if not plant:
            return None
        
        update_data = plant_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plant, field, value)
        
        self.db.commit()
        self.db.refresh(plant)
        return plant
    
    def delete_plant(self, plant_id: int, seller_id: int) -> bool:
        """Soft delete plant (deactivate)"""
        plant = self.db.query(Plant).filter(
            and_(Plant.id == plant_id, Plant.seller_id == seller_id)
        ).first()
        
        if not plant:
            return False
        
        plant.is_active = False
        self.db.commit()
        return True
    
    def get_seller_plants(self, seller_id: int, page: int = 1, size: int = 20) -> tuple[List[Plant], int]:
        """Get plants by seller"""
        query = self.db.query(Plant).filter(Plant.seller_id == seller_id)
        total = query.count()
        
        offset = (page - 1) * size
        plants = query.offset(offset).limit(size).all()
        
        return plants, total
    
    def update_plant_verification(self, plant_id: int, verified: bool) -> bool:
        """Update plant AI verification status"""
        plant = self.get_plant_by_id(plant_id)
        if not plant:
            return False
        
        plant.verified_by_ai = verified
        self.db.commit()
        return True
