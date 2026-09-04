from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.diagnosis import diagnose_payment
from app.database.dependencies import get_db
from app.models import Payment
from app.policy.engine import authorize_recovery
from app.schemas.payment import PaymentEvent


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def payment_view(payment: Payment) -> dict:
    diagnosis = diagnose_payment(
        failure_code=payment.failure_code,
        amount=payment.amount,
        customer_history=payment.customer_history,
        previous_failures=payment.retry_count,
    )

    authorized_action = authorize_recovery(
        diagnosis=diagnosis,
        retry_count=payment.retry_count,
        payment_already_processed=payment.status == "RECOVERED",
    )

    return {
        "id": payment.id,
        "payment_id": f"PAY-{payment.id:06d}",
        "amount": payment.amount,
        "currency": payment.currency,
        "customer_id": payment.customer_id,
        "failure_code": payment.failure_code,
        "status": payment.status,
        "retry_count": payment.retry_count,
        "customer_history": payment.customer_history,
        "previous_failures": payment.previous_failures,
        "recoverability": diagnosis.recoverability,
        "confidence": diagnosis.confidence,
        "failure_class": diagnosis.failure_class.value,
        "recommended_action": diagnosis.recommended_action.value,
        "authorized_action": authorized_action.value,
        "reason": diagnosis.reason,
        "created_at": payment.created_at,
    }


@router.post("/events")
def create_payment_event(
    event: PaymentEvent,
    db: Session = Depends(get_db),
):
    payment = Payment(
        amount=event.amount,
        currency=event.currency.upper(),
        customer_id=event.customer_id,
        failure_code=event.failure_code,
        status="FAILED",
        retry_count=0,
        customer_history=event.customer_history,
        previous_failures=event.previous_failures,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "id": payment.id,
        "status": payment.status,
        "message": "Payment failure event recorded",
    }


@router.get("")
def list_payments(
    limit: int = 50,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 100))

    query = select(Payment).order_by(
        Payment.created_at.desc()
    )

    if status:
        query = query.where(
            Payment.status == status.upper()
        )

    payments = db.scalars(
        query.limit(limit)
    ).all()

    return [
        payment_view(payment)
        for payment in payments
    ]


@router.get("/{payment_id}")
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = db.get(Payment, payment_id)

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment_view(payment)
