from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.diagnosis import diagnose_payment
from app.database.dependencies import get_db
from app.models import AuditLog, Diagnosis, Payment
from app.policy.engine import authorize_recovery
from app.schemas.recovery import ExecutionResult, RecoveryDecision
from app.services.executor import execute_recovery


router = APIRouter(
    prefix="/recovery",
    tags=["Recovery"],
)


def get_payment_or_404(
    payment_id: int,
    db: Session,
) -> Payment:
    payment = db.get(Payment, payment_id)

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment


@router.post(
    "/analyze/{payment_id}",
    response_model=RecoveryDecision,
)
def analyze_recovery(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = get_payment_or_404(payment_id, db)

    diagnosis = diagnose_payment(
        failure_code=payment.failure_code,
        amount=payment.amount,
        customer_history=payment.customer_history,
        previous_failures=payment.retry_count,
    )

    action = authorize_recovery(
        diagnosis=diagnosis,
        retry_count=payment.retry_count,
        payment_already_processed=payment.status == "RECOVERED",
    )

    diagnosis_record = Diagnosis(
        payment_id=payment.id,
        failure_class=diagnosis.failure_class.value,
        confidence=diagnosis.confidence,
        recoverability=diagnosis.recoverability,
        recommended_action=diagnosis.recommended_action.value,
        reason=diagnosis.reason,
    )

    db.add(diagnosis_record)

    policy_passed = action == diagnosis.recommended_action

    audit_record = AuditLog(
        payment_id=payment.id,
        event="RECOVERY_ANALYSIS",
        decision=action.value,
        reason=(
            "Recovery action authorized by deterministic policy."
            if policy_passed
            else "AI recommendation modified or blocked by deterministic policy."
        ),
    )

    db.add(audit_record)
    db.commit()

    return RecoveryDecision(
        payment_id=payment.id,
        diagnosis=diagnosis,
        authorized_action=action,
        policy_passed=policy_passed,
        reason=audit_record.reason,
    )


@router.post(
    "/execute/{payment_id}",
    response_model=ExecutionResult,
)
def execute_payment_recovery(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = get_payment_or_404(payment_id, db)

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

    result = execute_recovery(
        payment=payment,
        action=authorized_action,
        db=db,
    )

    return ExecutionResult(
        payment_id=payment.id,
        diagnosis=diagnosis,
        authorized_action=authorized_action,
        action=result.action,
        status=result.status,
        attempt=result.attempt,
        idempotency_key=result.idempotency_key,
    )
