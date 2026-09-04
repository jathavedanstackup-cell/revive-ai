import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
)


RAZORPAY_API_BASE = "https://api.razorpay.com/v1"


class RazorpayConfigurationError(Exception):
    pass


class RazorpayAPIError(Exception):
    pass


class RazorpayClient:
    def __init__(
        self,
        key_id: str | None = None,
        key_secret: str | None = None,
        timeout: float = 10.0,
    ):
        self.key_id = key_id or RAZORPAY_KEY_ID
        self.key_secret = key_secret or RAZORPAY_KEY_SECRET
        self.timeout = timeout

    def _ensure_credentials(self) -> None:
        if not self.key_id or not self.key_secret:
            raise RazorpayConfigurationError(
                "Razorpay credentials are not configured."
            )

    def _request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
    ) -> dict:
        self._ensure_credentials()

        credentials = (
            f"{self.key_id}:{self.key_secret}"
        ).encode("utf-8")

        encoded_credentials = base64.b64encode(
            credentials
        ).decode("ascii")

        headers = {
            "Authorization": (
                f"Basic {encoded_credentials}"
            ),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        body = None

        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        request = Request(
            url=f"{RAZORPAY_API_BASE}{path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw = response.read().decode("utf-8")

                if not raw:
                    return {}

                return json.loads(raw)

        except HTTPError as exc:
            raw = exc.read().decode("utf-8")

            try:
                detail = json.loads(raw)
            except json.JSONDecodeError:
                detail = {"message": raw}

            raise RazorpayAPIError(
                f"Razorpay API returned HTTP {exc.code}: {detail}"
            ) from exc

        except URLError as exc:
            raise RazorpayAPIError(
                f"Unable to reach Razorpay API: {exc.reason}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise RazorpayAPIError(
                "Razorpay returned invalid JSON."
            ) from exc

    def get_payment(self, payment_id: str) -> dict:
        return self._request(
            method="GET",
            path=f"/payments/{payment_id}",
        )

    def capture_payment(
        self,
        payment_id: str,
        amount: int | None = None,
    ) -> dict:
        payload = {}

        if amount is not None:
            payload["amount"] = amount

        return self._request(
            method="POST",
            path=f"/payments/{payment_id}/capture",
            payload=payload,
        )
