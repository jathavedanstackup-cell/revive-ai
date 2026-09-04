from app.database.session import Base, engine
from app.models import AuditLog, Diagnosis, Payment, RecoveryAction


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
