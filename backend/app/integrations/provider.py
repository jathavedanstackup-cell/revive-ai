from typing import Protocol


class PaymentProvider(Protocol):
    def get_payment(self, payment_id: str) -> dict:
        ...

    def capture_payment(
        self,
        payment_id: str,
        amount: int | None = None,
    ) -> dict:
        ...
