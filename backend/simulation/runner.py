import random

from app.ai.diagnosis import diagnose_failure
from app.policy.engine import authorize_recovery
from app.schemas.diagnosis import RecoveryAction
from simulation.generator import generate_payments


def run_simulation(
    count: int = 1000,
    seed: int = 42,
) -> dict:

    payments = generate_payments(
        count=count,
        seed=seed,
    )

    rng = random.Random(seed + 1)

    total_at_risk = 0.0
    recovered_revenue = 0.0
    retry_count = 0
    escalations = 0
    stopped = 0

    results = []

    for payment in payments:

        amount = payment["amount"]

        total_at_risk += amount

        diagnosis = diagnose_failure(
            payment["failure_code"]
        )

        action = authorize_recovery(
            diagnosis=diagnosis,
            retry_count=0,
            payment_already_processed=False,
        )

        recovered = False

        if action == RecoveryAction.RETRY_NOW:
            retry_count += 1

            recovered = (
                rng.random()
                < payment["recovery_probability"]
            )

        elif action == RecoveryAction.ESCALATE:
            escalations += 1

        elif action == RecoveryAction.STOP:
            stopped += 1

        if recovered:
            recovered_revenue += amount

        results.append(
            {
                "payment_id": payment["id"],
                "amount": amount,
                "failure_code": payment["failure_code"],
                "action": action.value,
                "recovered": recovered,
            }
        )

    recovery_rate = (
        recovered_revenue / total_at_risk
        if total_at_risk
        else 0.0
    )

    return {
        "total_payments": count,
        "total_revenue_at_risk": round(total_at_risk, 2),
        "recovered_revenue": round(recovered_revenue, 2),
        "recovery_rate": round(recovery_rate * 100, 2),
        "retry_count": retry_count,
        "escalations": escalations,
        "stopped": stopped,
        "results": results,
    }
