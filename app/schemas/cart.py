from pydantic import BaseModel, conint
from typing import List


class CartItemCreate(BaseModel):
    plant_id: int
    quantity: conint(gt=0)


class CartItemUpdate(BaseModel):
    quantity: conint(gt=0)


class CartItemResponse(BaseModel):
    id: int
    plant_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    total_quantity: int
    total_price: float

    class Config:
        from_attributes = True


