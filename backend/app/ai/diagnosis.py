from app.schemas.diagnosis import Diagnosis, FailureClass, RecoveryAction


FAILURE_MAP = {
    "issuer_timeout": (
        FailureClass.TRANSIENT_ISSUER_FAILURE,
        0.93,
        0.94,
        RecoveryAction.RETRY_NOW,
        "Transient issuer timeout is potentially recoverable.",
    ),
    "network_error": (
        FailureClass.NETWORK_FAILURE,
        0.90,
        0.92,
        RecoveryAction.RETRY_NOW,
        "Network failure may resolve on a subsequent attempt.",
    ),
    "insufficient_funds": (
        FailureClass.INSUFFICIENT_FUNDS,
        0.25,
        0.96,
        RecoveryAction.CUSTOMER_INTERVENTION,
        "Insufficient funds generally requires customer action.",
    ),
    "expired_card": (
        FailureClass.EXPIRED_PAYMENT_METHOD,
        0.15,
        0.98,
        RecoveryAction.CUSTOMER_INTERVENTION,
        "Expired payment method requires customer intervention.",
    ),
    "authentication_failed": (
        FailureClass.AUTHENTICATION_FAILURE,
        0.20,
        0.95,
        RecoveryAction.CUSTOMER_INTERVENTION,
        "Authentication failure should not be blindly retried.",
    ),
}


def diagnose_failure(failure_code: str) -> Diagnosis:
    result = FAILURE_MAP.get(failure_code.lower())

    if result is None:
        return Diagnosis(
            failure_class=FailureClass.UNKNOWN,
            recoverability=0.0,
            confidence=0.50,
            recommended_action=RecoveryAction.ESCALATE,
            reason="Unknown failure type requires controlled escalation.",
        )

    failure_class, recoverability, confidence, action, reason = result

    return Diagnosis(
        failure_class=failure_class,
        recoverability=recoverability,
        confidence=confidence,
        recommended_action=action,
        reason=reason,
    )


def diagnose_payment(
    failure_code: str,
    amount: float,
    customer_history: float,
    previous_failures: int,
) -> Diagnosis:
    diagnosis = diagnose_failure(failure_code)

    recoverability = diagnosis.recoverability
    confidence = diagnosis.confidence
    action = diagnosis.recommended_action

    if failure_code.lower() in {"issuer_timeout", "network_error"}:
        recoverability += (customer_history - 0.5) * 0.20
        recoverability -= previous_failures * 0.08

        if amount > 7500:
            confidence -= 0.04
            recoverability -= 0.05

        recoverability = max(0.0, min(1.0, recoverability))
        confidence = max(0.0, min(1.0, confidence))

        if recoverability < 0.80 or confidence < 0.85:
            action = RecoveryAction.ESCALATE

    return Diagnosis(
        failure_class=diagnosis.failure_class,
        recoverability=round(recoverability, 2),
        confidence=round(confidence, 2),
        recommended_action=action,
        reason=(
            f"Context-aware assessment using payment amount "
            f"INR {amount:.0f}, customer history {customer_history:.2f}, "
            f"and {previous_failures} previous failures."
        ),
    )



