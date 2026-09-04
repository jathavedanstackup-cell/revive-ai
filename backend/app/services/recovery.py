from sqlalchemy.orm import Session

from app.ai.diagnosis import diagnose_payment
from app.models import AuditLog, Diagnosis, Payment
from app.policy.engine import authorize_recovery
from app.schemas.recovery import RecoveryDecision


def analyze_payment(
    payment: Payment,
    db: Session,
) -> RecoveryDecision:

    diagnosis = diagnose_payment(
        failure_code=payment.failure_code,
        amount=payment.amount,
        customer_history=0.50,
        previous_failures=payment.retry_count,
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

    action = authorize_recovery(
        diagnosis=diagnosis,
        retry_count=payment.retry_count,
        payment_already_processed=payment.status == "SUCCESS",
    )

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
