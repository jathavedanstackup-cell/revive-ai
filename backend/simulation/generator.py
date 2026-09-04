import random

from simulation.scenarios import SCENARIOS


def generate_payments(count: int = 1000, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)

    total_probability = sum(
        scenario["probability"]
        for scenario in SCENARIOS
    )

    if abs(total_probability - 1.0) > 1e-9:
        raise ValueError(
            f"Scenario probabilities must sum to 1.0, got {total_probability}"
        )

    payments = []

    for payment_id in range(1, count + 1):
        roll = rng.random()

        cumulative = 0.0
        selected = SCENARIOS[-1]

        for scenario in SCENARIOS:
            cumulative += scenario["probability"]

            if roll <= cumulative:
                selected = scenario
                break

        amount = rng.randint(500, 10000)

        payments.append(
            {
                "id": payment_id,
                "amount": amount,
                "failure_code": selected["failure_code"],
                "retry_recovery_probability": (
                    selected["retry_recovery_probability"]
                ),
                "intervention_recovery_probability": (
                    selected["intervention_recovery_probability"]
                ),
                "customer_history": round(
                    rng.uniform(0.20, 0.99),
                    2,
                ),
                "previous_failures": rng.randint(0, 3),
                "retry_draw": rng.random(),
                "intervention_draw": rng.random(),
            }
        )

    return payments
