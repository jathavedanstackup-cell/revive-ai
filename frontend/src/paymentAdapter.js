export function normalizePayment(payment) {
  const actionMap = {
    RETRY_NOW: "RETRY NOW",
    RETRY_LATER: "RETRY LATER",
    CUSTOMER_INTERVENTION: "INTERVENE",
    ALTERNATE_PAYMENT_METHOD: "ALTERNATE METHOD",
    STOP: "STOP",
    ESCALATE: "ESCALATE",
  };

  return {
    id: payment.id,
    paymentId: payment.payment_id,
    amount: payment.amount,
    currency: payment.currency,
    customerId: payment.customer_id,
    failure: payment.failure_class.replaceAll("_", " "),
    failureCode: payment.failure_code,
    recoverability: Math.round(payment.recoverability * 100),
    confidence: Math.round(payment.confidence * 100),
    action: actionMap[payment.authorized_action] || payment.authorized_action,
    status: payment.status,
    customerHistory:
      payment.customer_history >= 0.75
        ? "Strong"
        : payment.customer_history >= 0.50
          ? "Moderate"
          : "Weak",
    previousFailures: payment.previous_failures,
    reason: payment.reason,
  };
}
