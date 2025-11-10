import time
from sqlalchemy.orm import Session
from app.models import Payment, PaymentStatus, Order, OrderStatus


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_razorpay_order(self, order_id: int) -> Payment:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        payment = Payment(
            order_id=order_id,
            provider="razorpay",
            status=PaymentStatus.PENDING,
            amount=order.total_price,
            currency="INR",
            provider_order_id=f"order_{int(time.time()*1000)}_{order_id}",
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def mark_cod_confirmed(self, order_id: int) -> Payment:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        payment = Payment(
            order_id=order_id,
            provider="cod",
            status=PaymentStatus.SUCCESS,
            amount=order.total_price,
            currency="INR",
        )
        order.status = OrderStatus.CONFIRMED
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def handle_razorpay_webhook(self, provider_order_id: str, provider_payment_id: str, status: str, signature: str | None = None) -> bool:
        payment = self.db.query(Payment).filter(Payment.provider_order_id == provider_order_id).first()
        if not payment:
            return False
        if status.lower() == "paid":
            payment.status = PaymentStatus.SUCCESS
            payment.provider_payment_id = provider_payment_id
            payment.provider_signature = signature
            order = self.db.query(Order).filter(Order.id == payment.order_id).first()
            if order:
                order.status = OrderStatus.CONFIRMED
        else:
            payment.status = PaymentStatus.FAILED
        self.db.commit()
        return True


