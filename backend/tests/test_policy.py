import unittest

from app.ai.diagnosis import diagnose_payment
from app.policy.engine import authorize_recovery


class PolicyTests(unittest.TestCase):

    def test_recovered_payment_is_stopped(self):
        diagnosis = diagnose_payment(
            failure_code="issuer_timeout",
            amount=7499,
            customer_history=0.92,
            previous_failures=1,
        )

        action = authorize_recovery(
            diagnosis=diagnosis,
            retry_count=1,
            payment_already_processed=True,
        )

        self.assertEqual(
            action.value,
            "STOP",
        )

    def test_retry_budget_is_bounded(self):
        diagnosis = diagnose_payment(
            failure_code="network_error",
            amount=4200,
            customer_history=0.88,
            previous_failures=2,
        )

        action = authorize_recovery(
            diagnosis=diagnosis,
            retry_count=2,
            payment_already_processed=False,
        )

        self.assertEqual(
            action.value,
            "ESCALATE",
        )


if __name__ == "__main__":
    unittest.main()
