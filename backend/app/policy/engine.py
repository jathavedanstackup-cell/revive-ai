from app.schemas.diagnosis import Diagnosis, RecoveryAction


MIN_CONFIDENCE = 0.85
MIN_RECOVERABILITY = 0.80
MAX_RETRIES = 2


def authorize_recovery(
    diagnosis: Diagnosis,
    retry_count: int,
    payment_already_processed: bool = False,
) -> RecoveryAction:

    if payment_already_processed:
        return RecoveryAction.STOP

    if retry_count >= MAX_RETRIES:
        return RecoveryAction.ESCALATE

    if diagnosis.confidence < MIN_CONFIDENCE:
        return RecoveryAction.ESCALATE

    if diagnosis.recoverability < MIN_RECOVERABILITY:
        return diagnosis.recommended_action

    if diagnosis.recommended_action == RecoveryAction.RETRY_NOW:
        return RecoveryAction.RETRY_NOW

    return diagnosis.recommended_action
