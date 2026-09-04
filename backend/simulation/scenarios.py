SCENARIOS = [
    {
        "failure_code": "issuer_timeout",
        "probability": 0.25,
        "retry_recovery_probability": 0.80,
        "intervention_recovery_probability": 0.08,
    },
    {
        "failure_code": "network_error",
        "probability": 0.15,
        "retry_recovery_probability": 0.75,
        "intervention_recovery_probability": 0.05,
    },
    {
        "failure_code": "insufficient_funds",
        "probability": 0.25,
        "retry_recovery_probability": 0.03,
        "intervention_recovery_probability": 0.55,
    },
    {
        "failure_code": "expired_card",
        "probability": 0.15,
        "retry_recovery_probability": 0.00,
        "intervention_recovery_probability": 0.68,
    },
    {
        "failure_code": "authentication_failed",
        "probability": 0.10,
        "retry_recovery_probability": 0.02,
        "intervention_recovery_probability": 0.45,
    },
    {
        "failure_code": "unknown",
        "probability": 0.10,
        "retry_recovery_probability": 0.00,
        "intervention_recovery_probability": 0.20,
    },
]
