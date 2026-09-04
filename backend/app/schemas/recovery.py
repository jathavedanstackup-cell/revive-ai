from pydantic import BaseModel

from app.schemas.diagnosis import Diagnosis, RecoveryAction


class RecoveryDecision(BaseModel):
    payment_id: int
    diagnosis: Diagnosis
    authorized_action: RecoveryAction
    policy_passed: bool
    reason: str


class ExecutionResult(BaseModel):
    payment_id: int
    diagnosis: Diagnosis
    authorized_action: RecoveryAction
    action: str
    status: str
    attempt: int
    idempotency_key: str
