from datetime import datetime

from sqlalchemy.orm import Session

from app.models import AuditLog, Payment, RecoveryAction
from app.schemas.diagnosis import RecoveryAction as RecoveryActionType


MAX_RETRIES = 2


def simulate_retry_result(payment: Payment) -> bool:
    """
    Controlled simulation only.

    In the demo environment, transient issuer and network failures
    are modeled as recoverable through a bounded retry.
    """
    return payment.failure_code in {
        "issuer_timeout",
        "network_error",
    }


def execute_recovery(
    payment: Payment,
    action: RecoveryActionType,
    db: Session,
) -> RecoveryAction:

    next_attempt = payment.retry_count + 1

    idempotency_key = (
        f"payment-{payment.id}-attempt-{next_attempt}"
    )

    existing = (
        db.query(RecoveryAction)
        .filter(
            RecoveryAction.idempotency_key
            == idempotency_key
        )
        .first()
    )

    if existing:
        return existing

    if payment.status == "RECOVERED":
        action = RecoveryActionType.STOP

    if action == RecoveryActionType.RETRY_NOW:
        if payment.retry_count >= MAX_RETRIES:
            action = RecoveryActionType.ESCALATE

    if action == RecoveryActionType.RETRY_NOW:
        payment.retry_count += 1

        recovered = simulate_retry_result(payment)

        if recovered:
            payment.status = "RECOVERED"
            status = "SUCCESS"
            reason = (
                "Simulated bounded retry recovered the payment."
            )
        else:
            status = "FAILED"
            reason = (
                "Simulated retry did not recover the payment."
            )

        attempt = payment.retry_count

    elif action == RecoveryActionType.ESCALATE:
        status = "ESCALATED"
        attempt = 0
        reason = (
            "Recovery stopped by policy and requires controlled escalation."
        )

    else:
        status = "STOPPED"
        attempt = 0
        reason = (
            "No financial execution permitted for this action."
        )

    record = RecoveryAction(
        payment_id=payment.id,
        action=action.value,
        status=status,
        attempt=attempt,
        idempotency_key=idempotency_key,
        executed_at=datetime.utcnow(),
    )

    db.add(record)

    db.add(
        AuditLog(
            payment_id=payment.id,
            event="RECOVERY_EXECUTION",
            decision=action.value,
            reason=reason,
        )
    )

    db.commit()
    db.refresh(record)

    return record
