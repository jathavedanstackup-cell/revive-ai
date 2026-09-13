import json
from pathlib import Path

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Payment

SAMPLE_PAYMENTS_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "sample_payments.json"
)


def seed_demo_payments() -> None:
    db = SessionLocal()

    try:
        existing = db.scalars(select(Payment.id).limit(1)).first()

        if existing is not None:
            return

        if not SAMPLE_PAYMENTS_PATH.exists():
            return

        records = json.loads(SAMPLE_PAYMENTS_PATH.read_text(encoding="utf-8-sig"))

        for index, record in enumerate(records, start=1):
            db.add(
                Payment(
                    amount=record["amount"],
                    currency=record.get("currency", "INR"),
                    customer_id=f"CUST-{index:04d}",
                    failure_code=record["failure_code"],
                    status=record.get("status", "FAILED"),
                    retry_count=0,
                    customer_history=record.get("customer_history", 0.50),
                    previous_failures=record.get("previous_failures", 0),
                )
            )

        db.commit()

    finally:
        db.close()
