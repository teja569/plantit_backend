from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.payments import RazorpayOrderRequest, RazorpayOrderResponse, RazorpayWebhookPayload, CODConfirmRequest
from app.services.payment_service import PaymentService
from app.models import User


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/razorpay/order", response_model=RazorpayOrderResponse)
async def create_razorpay_order(
    body: RazorpayOrderRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    svc = PaymentService(db)
    try:
        payment = svc.create_razorpay_order(body.order_id)
        return RazorpayOrderResponse(
            amount=payment.amount,
            currency=payment.currency,
            provider_order_id=payment.provider_order_id,
            receipt=f"order_{payment.order_id}"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/razorpay/webhook")
async def razorpay_webhook(
    payload: RazorpayWebhookPayload,
    db: Session = Depends(get_db)
):
    svc = PaymentService(db)
    ok = svc.handle_razorpay_webhook(
        provider_order_id=payload.provider_order_id,
        provider_payment_id=payload.provider_payment_id,
        status=payload.status,
        signature=payload.provider_signature,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"status": "ok"}


@router.post("/cod/confirm")
async def cod_confirm(
    body: CODConfirmRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    svc = PaymentService(db)
    try:
        payment = svc.mark_cod_confirmed(body.order_id)
        return {"message": "COD confirmed", "order_id": payment.order_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


