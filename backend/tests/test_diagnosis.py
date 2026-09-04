import unittest

from app.ai.diagnosis import diagnose_payment


class DiagnosisTests(unittest.TestCase):

    def test_network_failure_is_retryable(self):
        result = diagnose_payment(
            failure_code="network_error",
            amount=4200,
            customer_history=0.88,
            previous_failures=0,
        )

        self.assertEqual(
            result.failure_class.value,
            "NETWORK_FAILURE",
        )

        self.assertEqual(
            result.recommended_action.value,
            "RETRY_NOW",
        )

    def test_insufficient_funds_requires_intervention(self):
        result = diagnose_payment(
            failure_code="insufficient_funds",
            amount=3200,
            customer_history=0.68,
            previous_failures=1,
        )

        self.assertEqual(
            result.recommended_action.value,
            "CUSTOMER_INTERVENTION",
        )

    def test_unknown_failure_escalates(self):
        result = diagnose_payment(
            failure_code="unknown",
            amount=9800,
            customer_history=0.31,
            previous_failures=2,
        )

        self.assertEqual(
            result.recommended_action.value,
            "ESCALATE",
        )


if __name__ == "__main__":
    unittest.main()
