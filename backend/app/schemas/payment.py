from pydantic import BaseModel, Field


class PaymentEvent(BaseModel):
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    customer_id: str = Field(min_length=1, max_length=100)
    failure_code: str = Field(min_length=1, max_length=100)
    customer_history: float = Field(default=0.50, ge=0, le=1)
    previous_failures: int = Field(default=0, ge=0)
