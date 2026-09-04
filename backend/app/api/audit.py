from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models import AuditLog


router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


@router.get("")
def list_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 200))

    logs = db.scalars(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    ).all()

    return [
        {
            "id": log.id,
            "payment_id": log.payment_id,
            "event": log.event,
            "decision": log.decision,
            "reason": log.reason,
            "created_at": log.created_at,
        }
        for log in logs
    ]
