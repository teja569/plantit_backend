from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Tuple
from app.models import Cart, CartItem, Plant, ApprovalStatus


class CartService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_cart(self, user_id: int) -> Cart:
        cart = self.db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        return cart

    def get_cart(self, user_id: int) -> Tuple[Cart, int, float]:
        cart = self._get_or_create_cart(user_id)
        total_qty = sum(item.quantity for item in cart.items)
        total_price = sum(item.quantity * item.unit_price for item in cart.items)
        return cart, total_qty, total_price

    def add_item(self, user_id: int, plant_id: int, quantity: int) -> Cart:
        cart = self._get_or_create_cart(user_id)
        plant = self.db.query(Plant).filter(
            and_(Plant.id == plant_id, Plant.is_active == True, Plant.approval_status == ApprovalStatus.APPROVED)
        ).first()
        if not plant:
            raise ValueError("Product not available")
        if plant.stock_quantity < quantity:
            raise ValueError("Insufficient stock")
        existing = next((i for i in cart.items if i.plant_id == plant_id), None)
        if existing:
            new_qty = existing.quantity + quantity
            if plant.stock_quantity < new_qty:
                raise ValueError("Insufficient stock")
            existing.quantity = new_qty
        else:
            cart.items.append(CartItem(plant_id=plant_id, quantity=quantity, unit_price=plant.price))
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def update_item(self, user_id: int, item_id: int, quantity: int) -> Cart:
        cart = self._get_or_create_cart(user_id)
        item = next((i for i in cart.items if i.id == item_id), None)
        if not item:
            raise ValueError("Item not found")
        plant = self.db.query(Plant).filter(Plant.id == item.plant_id).first()
        if not plant or plant.stock_quantity < quantity:
            raise ValueError("Insufficient stock")
        item.quantity = quantity
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def remove_item(self, user_id: int, item_id: int) -> Cart:
        cart = self._get_or_create_cart(user_id)
        item = next((i for i in cart.items if i.id == item_id), None)
        if not item:
            raise ValueError("Item not found")
        self.db.delete(item)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def clear_cart(self, user_id: int) -> Cart:
        cart = self._get_or_create_cart(user_id)
        for item in list(cart.items):
            self.db.delete(item)
        self.db.commit()
        self.db.refresh(cart)
        return cart


