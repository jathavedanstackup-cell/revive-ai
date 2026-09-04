from enum import Enum

from pydantic import BaseModel, Field


class FailureClass(str, Enum):
    TRANSIENT_ISSUER_FAILURE = "TRANSIENT_ISSUER_FAILURE"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    EXPIRED_PAYMENT_METHOD = "EXPIRED_PAYMENT_METHOD"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    UNKNOWN = "UNKNOWN"


class RecoveryAction(str, Enum):
    RETRY_NOW = "RETRY_NOW"
    RETRY_LATER = "RETRY_LATER"
    CUSTOMER_INTERVENTION = "CUSTOMER_INTERVENTION"
    ALTERNATE_PAYMENT_METHOD = "ALTERNATE_PAYMENT_METHOD"
    STOP = "STOP"
    ESCALATE = "ESCALATE"


class Diagnosis(BaseModel):
    failure_class: FailureClass
    recoverability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    recommended_action: RecoveryAction
    reason: str
