from app.ai.diagnosis import diagnose_payment
from app.policy.engine import authorize_recovery
from app.schemas.diagnosis import RecoveryAction
from simulation.generator import generate_payments


RETRY_COST = 2.0
INTERVENTION_COST = 8.0


def prepare_batch(count: int = 1000, seed: int = 42) -> list[dict]:
    return generate_payments(
        count=count,
        seed=seed,
    )


def blind_retry(payments: list[dict]) -> dict:
    at_risk = sum(payment["amount"] for payment in payments)
    recovered = 0.0
    retries = 0
    recovery_cost = 0.0

    for payment in payments:
        retries += 1
        recovery_cost += RETRY_COST

        if (
            payment["retry_draw"]
            < payment["retry_recovery_probability"]
        ):
            recovered += payment["amount"]

    return {
        "recovered_revenue": round(recovered, 2),
        "recovery_rate": round(
            (recovered / at_risk) * 100,
            2,
        ),
        "retries": retries,
        "interventions": 0,
        "recovery_cost": round(recovery_cost, 2),
        "net_recovered_revenue": round(
            recovered - recovery_cost,
            2,
        ),
    }


def static_rules(payments: list[dict]) -> dict:
    at_risk = sum(payment["amount"] for payment in payments)
    recovered = 0.0
    retries = 0
    recovery_cost = 0.0

    retryable = {
        "issuer_timeout",
        "network_error",
    }

    for payment in payments:
        if payment["failure_code"] in retryable:
            retries += 1
            recovery_cost += RETRY_COST

            if (
                payment["retry_draw"]
                < payment["retry_recovery_probability"]
            ):
                recovered += payment["amount"]

    return {
        "recovered_revenue": round(recovered, 2),
        "recovery_rate": round(
            (recovered / at_risk) * 100,
            2,
        ),
        "retries": retries,
        "interventions": 0,
        "recovery_cost": round(recovery_cost, 2),
        "net_recovered_revenue": round(
            recovered - recovery_cost,
            2,
        ),
    }


def revive_ai(payments: list[dict]) -> dict:
    at_risk = sum(payment["amount"] for payment in payments)

    recovered = 0.0
    retries = 0
    interventions = 0
    escalations = 0
    stopped = 0
    recovery_cost = 0.0

    for payment in payments:
        diagnosis = diagnose_payment(
            failure_code=payment["failure_code"],
            amount=payment["amount"],
            customer_history=payment["customer_history"],
            previous_failures=payment["previous_failures"],
        )

        action = authorize_recovery(
            diagnosis=diagnosis,
            retry_count=0,
            payment_already_processed=False,
        )

        if action == RecoveryAction.RETRY_NOW:
            retries += 1
            recovery_cost += RETRY_COST

            if (
                payment["retry_draw"]
                < payment["retry_recovery_probability"]
            ):
                recovered += payment["amount"]

        elif action == RecoveryAction.CUSTOMER_INTERVENTION:
            interventions += 1
            recovery_cost += INTERVENTION_COST

            adjusted_probability = (
                payment["intervention_recovery_probability"]
                * (0.70 + 0.30 * payment["customer_history"])
                * max(
                    0.70,
                    1.0 - (payment["previous_failures"] * 0.10),
                )
            )

            if payment["intervention_draw"] < adjusted_probability:
                recovered += payment["amount"]

        elif action == RecoveryAction.ESCALATE:
            escalations += 1

        elif action == RecoveryAction.STOP:
            stopped += 1

    return {
        "recovered_revenue": round(recovered, 2),
        "recovery_rate": round(
            (recovered / at_risk) * 100,
            2,
        ),
        "retries": retries,
        "interventions": interventions,
        "escalations": escalations,
        "stopped": stopped,
        "recovery_cost": round(recovery_cost, 2),
        "net_recovered_revenue": round(
            recovered - recovery_cost,
            2,
        ),
    }


def run_benchmark(
    count: int = 1000,
    seed: int = 42,
) -> dict:
    payments = prepare_batch(
        count=count,
        seed=seed,
    )

    return {
        "batch_size": count,
        "blind_retry": blind_retry(payments),
        "static_rules": static_rules(payments),
        "revive_ai": revive_ai(payments),
    }
