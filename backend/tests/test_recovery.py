import unittest

from app.services.executor import simulate_retry_result


class RecoveryTests(unittest.TestCase):

    def test_transient_failures_are_simulated_as_recoverable(self):
        self.assertTrue(
            simulate_retry_result(
                type(
                    "PaymentStub",
                    (),
                    {"failure_code": "network_error"},
                )()
            )
        )

        self.assertTrue(
            simulate_retry_result(
                type(
                    "PaymentStub",
                    (),
                    {"failure_code": "issuer_timeout"},
                )()
            )
        )

    def test_unknown_failure_is_not_auto_recovered(self):
        self.assertFalse(
            simulate_retry_result(
                type(
                    "PaymentStub",
                    (),
                    {"failure_code": "unknown"},
                )()
            )
        )


if __name__ == "__main__":
    unittest.main()
