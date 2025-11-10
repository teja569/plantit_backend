from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from app.services.cart_service import CartService
from app.models import User


router = APIRouter(prefix="/cart", tags=["cart"])


def _to_response(cart, total_qty: int, total_price: float) -> CartResponse:
    return CartResponse(
        id=cart.id,
        items=[CartItemResponse.from_orm(i) for i in cart.items],
        total_quantity=total_qty,
        total_price=total_price,
    )


@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = CartService(db)
    cart, tq, tp = service.get_cart(current_user.id)
    return _to_response(cart, tq, tp)


@router.post("/items", response_model=CartResponse)
async def add_item(
    item: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = CartService(db)
    try:
        cart = service.add_item(current_user.id, item.plant_id, item.quantity)
        _, tq, tp = service.get_cart(current_user.id)
        return _to_response(cart, tq, tp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_item(
    item_id: int,
    body: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = CartService(db)
    try:
        cart = service.update_item(current_user.id, item_id, body.quantity)
        _, tq, tp = service.get_cart(current_user.id)
        return _to_response(cart, tq, tp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = CartService(db)
    try:
        cart = service.remove_item(current_user.id, item_id)
        _, tq, tp = service.get_cart(current_user.id)
        return _to_response(cart, tq, tp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/clear", response_model=CartResponse)
async def clear_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = CartService(db)
    cart = service.clear_cart(current_user.id)
    _, tq, tp = service.get_cart(current_user.id)
    return _to_response(cart, tq, tp)


