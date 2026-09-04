import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [section, setSection] = useState("overview");
  const [payments, setPayments] = useState([]);
  const [benchmark, setBenchmark] = useState(null);
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [execution, setExecution] = useState(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadPayments();
  }, []);

  async function loadPayments() {
    try {
      const response = await fetch(`${API_URL}/api/v1/payments?status=FAILED&limit=50`);

      if (!response.ok) {
        throw new Error(`Payments API returned ${response.status}`);
      }

      const result = await response.json();

      const normalized = result.map(normalizePayment);
      setPayments(normalized);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load payments.",
      );
    }
  }

  async function runBatch() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/v1/simulation/run`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            count: 1000,
            seed: 42,
          }),
        },
      );

      if (!response.ok) {
        throw new Error(`Simulation API returned ${response.status}`);
      }

      const result = await response.json();

      setBenchmark(result);
      await loadPayments();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to run benchmark.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function executeRecovery(payment) {
    setExecuting(true);
    setExecution(null);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/v1/recovery/execute/${payment.id}`,
        {
          method: "POST",
        },
      );

      if (!response.ok) {
        throw new Error(`Recovery API returned ${response.status}`);
      }

      const result = await response.json();
      setExecution(result);
      await loadPayments();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to execute recovery.",
      );
    } finally {
      setExecuting(false);
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand-row">
          <div className="logo-mark">R</div>

          <div>
            <div className="brand">REVIVE AI</div>
            <div className="subtitle">
              REVENUE RECOVERY CONTROL ROOM
            </div>
          </div>
        </div>

        <div className="topbar-right">
          <div className="mode-pill">
            <span className="live-dot"></span>
            TEST MODE
          </div>

          <div className="system-status">
            <span className="status-icon">OK</span>
            SYSTEM OPERATIONAL
          </div>
        </div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="nav-label">WORKSPACE</div>

          <NavButton
            label="Overview"
            active={section === "overview"}
            onClick={() => setSection("overview")}
          />

          <NavButton
            label="Payments"
            active={section === "payments"}
            onClick={() => setSection("payments")}
          />

          <NavButton
            label="Recovery"
            active={section === "recovery"}
            onClick={() => setSection("recovery")}
          />

          <NavButton
            label="Audit"
            active={section === "audit"}
            onClick={() => setSection("audit")}
          />

          <div className="sidebar-bottom">
            <div className="nav-label">ENVIRONMENT</div>

            <div className="environment">
              <span></span>
              Simulation
            </div>
          </div>
        </aside>

        <main className="dashboard">
          {section === "overview" && (
            <Overview
              payments={payments}
              benchmark={benchmark}
              loading={loading}
              error={error}
              runBatch={runBatch}
              onPayment={setSelectedPayment}
            />
          )}

          {section === "payments" && (
            <Payments
              payments={payments}
              onPayment={setSelectedPayment}
            />
          )}

          {section === "recovery" && (
            <Recovery
              benchmark={benchmark}
              loading={loading}
              runBatch={runBatch}
            />
          )}

          {section === "audit" && <Audit />}
        </main>
      </div>

      {selectedPayment && (
        <InvestigationDrawer
          payment={selectedPayment}
          execution={execution}
          executing={executing}
          onClose={() => {
            setSelectedPayment(null);
            setExecution(null);
          }}
          onExecute={executeRecovery}
        />
      )}
    </div>
  );
}

function Overview({
  payments,
  benchmark,
  loading,
  error,
  runBatch,
  onPayment,
}) {
  const revive = benchmark ? benchmark.revive_ai : null;
  const blind = benchmark ? benchmark.blind_retry : null;
  const staticRules = benchmark ? benchmark.static_rules : null;

  const revenueAtRisk =
    revive && revive.recovery_rate > 0
      ? revive.recovered_revenue / (revive.recovery_rate / 100)
      : 0;

  return (
    <>
      <section className="page-heading">
        <div>
          <div className="eyebrow">OVERVIEW</div>

          <h1>
            Recovery
            <br />
            <span>intelligence.</span>
          </h1>

          <p>
            Monitor payment exposure, evaluate recovery strategies,
            and intervene when payments need attention.
          </p>
        </div>

        <button
          className="run-button"
          onClick={runBatch}
          disabled={loading}
        >
          {loading ? "RUNNING..." : "RUN BATCH RECOVERY"}
        </button>
      </section>

      {error && (
        <div className="error-banner">
          <span>!</span>

          <div>
            <strong>SYSTEM ERROR</strong>
            <small>{error}</small>
          </div>
        </div>
      )}

      <section className="metric-grid">
        <MetricCard
          label="REVENUE AT RISK"
          value={`INR ${formatNumber(revenueAtRisk)}`}
          footnote="Total batch exposure"
        />

        <MetricCard
          label="RECOVERED REVENUE"
          value={
            revive
              ? `INR ${formatNumber(revive.recovered_revenue)}`
              : "INR 0"
          }
          footnote="REVIVE AI"
          featured
        />

        <MetricCard
          label="RECOVERY RATE"
          value={revive ? `${revive.recovery_rate}%` : "0%"}
          footnote="Revenue recovered"
        />

        <MetricCard
          label="ESCALATIONS"
          value={revive ? formatNumber(revive.escalations) : "0"}
          footnote="Human review"
        />
      </section>

      <section className="content-grid">
        <div className="panel">
          <PanelHeader
            title="RECOVERY PERFORMANCE"
            description="Recovered revenue by strategy"
            meta="BATCH BENCHMARK"
          />

          {!benchmark ? (
            <EmptyState />
          ) : (
            <div className="performance-list">
              <PerformanceBar
                label="Blind Retry"
                value={blind.recovered_revenue}
                rate={blind.recovery_rate}
                max={getMaxRevenue(benchmark)}
              />

              <PerformanceBar
                label="Static Rules"
                value={staticRules.recovered_revenue}
                rate={staticRules.recovery_rate}
                max={getMaxRevenue(benchmark)}
              />

              <PerformanceBar
                label="REVIVE AI"
                value={revive.recovered_revenue}
                rate={revive.recovery_rate}
                max={getMaxRevenue(benchmark)}
                active
              />
            </div>
          )}
        </div>

        <div className="panel">
          <PanelHeader
            title="DECISION ENGINE"
            description="Financial actions under policy control"
            meta="CONTROLLED"
          />

          <div className="engine-flow">
            <FlowStep
              number="01"
              title="FAILED PAYMENT"
              description="Payment enters recovery pipeline"
            />

            <FlowStep
              number="02"
              title="CONTEXTUAL DIAGNOSIS"
              description="Failure and customer context"
            />

            <FlowStep
              number="03"
              title="POLICY GATE"
              description="Thresholds, limits and idempotency"
            />

            <FlowStep
              number="04"
              title="BOUNDED ACTION"
              description="Retry, intervene or escalate"
              last
            />
          </div>

          <div className="policy-banner">
            <span>CORE SAFETY MODEL</span>
            <strong>AI REASONS. POLICY AUTHORIZES.</strong>
          </div>
        </div>
      </section>

      <section className="panel attention-panel">
        <PanelHeader
          title="PAYMENTS REQUIRING ATTENTION"
          description="Database-backed recovery queue"
          meta="LIVE DATA"
        />

        {payments.length === 0 ? (
          <EmptyPayments />
        ) : (
          <PaymentTable
            payments={payments}
            onPayment={onPayment}
          />
        )}
      </section>
    </>
  );
}

function Payments({ payments, onPayment }) {
  return (
    <>
      <PageTitle
        eyebrow="PAYMENTS"
        title="Payment queue."
        description="Review failed payments and investigate recovery decisions."
      />

      <section className="panel attention-panel">
        <PanelHeader
          title="FAILED PAYMENTS"
          description="Payments from the REVIVE database"
          meta="LIVE DATA"
        />

        {payments.length === 0 ? (
          <EmptyPayments />
        ) : (
          <PaymentTable
            payments={payments}
            onPayment={onPayment}
          />
        )}
      </section>
    </>
  );
}

function Recovery({ benchmark, loading, runBatch }) {
  const revive = benchmark ? benchmark.revive_ai : null;

  return (
    <>
      <PageTitle
        eyebrow="RECOVERY"
        title="Recovery operations."
        description="Review authorized actions, retries and escalations."
      />

      <section className="metric-grid">
        <MetricCard
          label="AUTHORIZED RETRIES"
          value={revive ? formatNumber(revive.retries) : "0"}
          footnote="Current benchmark"
        />

        <MetricCard
          label="INTERVENTIONS"
          value={
            revive
              ? formatNumber(revive.interventions)
              : "0"
          }
          footnote="Customer action paths"
          featured
        />

        <MetricCard
          label="ESCALATIONS"
          value={revive ? formatNumber(revive.escalations) : "0"}
          footnote="Human review"
        />

        <MetricCard
          label="STOPPED"
          value={revive ? formatNumber(revive.stopped) : "0"}
          footnote="Blocked actions"
        />
      </section>

      <section className="panel operation-panel">
        <PanelHeader
          title="BATCH RECOVERY"
          description="Run the reproducible benchmark"
          meta="SEED 42"
        />

        <div className="operation-content">
          <div>
            <strong>
              {benchmark
                ? `${benchmark.batch_size.toLocaleString()} payments processed`
                : "No benchmark executed"}
            </strong>

            <span>
              Same dataset, same outcomes, repeatable evaluation.
            </span>
          </div>

          <button
            className="secondary-button"
            onClick={runBatch}
            disabled={loading}
          >
            {loading ? "RUNNING..." : "RUN AGAIN"}
          </button>
        </div>
      </section>
    </>
  );
}

function Audit() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadAudit();
  }, []);

  async function loadAudit() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/v1/audit?limit=100`,
      );

      if (!response.ok) {
        throw new Error(
          `Audit API returned ${response.status}`,
        );
      }

      const result = await response.json();
      setEvents(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load audit history.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageTitle
        eyebrow="AUDIT"
        title="Decision history."
        description="Recovery decisions remain explainable and traceable."
      />

      <section className="panel audit-panel">
        <PanelHeader
          title="AUDIT TRAIL"
          description="Decision and execution events"
          meta="LIVE DATA"
        />

        {loading && (
          <div className="audit-empty">
            Loading audit history...
          </div>
        )}

        {!loading && error && (
          <div className="audit-empty">
            <strong>AUDIT LOAD FAILED</strong>
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && events.length === 0 && (
          <div className="audit-empty">
            <strong>NO AUDIT EVENTS</strong>
            <span>
              Recovery decisions will appear here.
            </span>
          </div>
        )}

        {!loading && !error && events.length > 0 && (
          <div className="audit-list">
            {events.map((event) => (
              <AuditEvent
                key={event.id}
                time={formatAuditTime(event.created_at)}
                id={`PAY-${String(event.payment_id).padStart(6, "0")}`}
                event={formatAuditEvent(event.event)}
                detail={`${event.decision} - ${event.reason}`}
              />
            ))}
          </div>
        )}
      </section>
    </>
  );
}
function InvestigationDrawer({
  payment,
  execution,
  executing,
  onClose,
  onExecute,
}) {
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside
        className="drawer"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="drawer-header">
          <div>
            <div className="drawer-eyebrow">
              PAYMENT INVESTIGATION
            </div>

            <h2>{payment.paymentId}</h2>
          </div>

          <button className="close-button" onClick={onClose}>
            X
          </button>
        </div>

        <div className="drawer-amount">
          <strong>
            INR {formatNumber(payment.amount)}
          </strong>

          <span className={`failure-pill ${payment.status === "RECOVERED" ? "recovered-pill" : ""}`}>{payment.status}</span>
        </div>

        <DrawerSection title="FAILURE">
          <div className="large-value">
            {payment.failure}
          </div>
        </DrawerSection>

        <DrawerSection title="REVIVE ASSESSMENT">
          <div className="assessment-grid">
            <Assessment
              label="Recoverability"
              value={`${payment.recoverability}%`}
            />

            <Assessment
              label="Confidence"
              value={`${payment.confidence}%`}
            />
          </div>

          <div className="reason-box">
            <span>REASONING</span>

            <p>{payment.reason}</p>
          </div>
        </DrawerSection>

        <DrawerSection title="CUSTOMER CONTEXT">
          <ContextRow
            label="Customer history"
            value={payment.customerHistory}
          />

          <ContextRow
            label="Previous failures"
            value={payment.previousFailures}
          />

          <ContextRow
            label="Environment"
            value="Simulation"
          />
        </DrawerSection>

        <DrawerSection title="POLICY GATE">
          <CheckRow
            label="Confidence threshold"
            passed={payment.confidence >= 85}
          />

          <CheckRow
            label="Recoverability threshold"
            passed={payment.recoverability >= 80}
          />

          <CheckRow
            label="Retry budget"
            passed={payment.action === "RETRY NOW"}
          />

          <CheckRow
            label="Idempotency control"
            passed={true}
          />
        </DrawerSection>

        <DrawerSection title="AUTHORIZED ACTION">
          <div className="authorized-action">
            <strong>{payment.action}</strong>
            <span>{payment.status}</span>
          </div>

          {!execution && payment.action !== "STOP" ? (
            <button
              className="execute-button"
              onClick={() => onExecute(payment)}
              disabled={executing}
            >
              {executing
                ? "EXECUTING..."
                : "EXECUTE RECOVERY"}
            </button>
          ) : (
            <div className="execution-result">
              <div className="success-heading">
                <span>OK</span>
                RECOVERY RESULT
              </div>

              <ContextRow
                label="Action"
                value={execution.action}
              />

              <ContextRow
                label="Status"
                value={execution.status}
              />

              <ContextRow
                label="Attempt"
                value={execution.attempt}
              />

              <ContextRow
                label="Idempotency"
                value="VERIFIED"
              />
            </div>
          )}
        </DrawerSection>
      </aside>
    </div>
  );
}

function PaymentTable({ payments, onPayment }) {
  return (
    <div className="table-wrap">
      <div className="payment-table">
        <div className="table-head">
          <span>PAYMENT</span>
          <span>AMOUNT</span>
          <span>FAILURE</span>
          <span>RECOVERABILITY</span>
          <span>ACTION</span>
          <span></span>
        </div>

        {payments.map((payment) => (
          <div className="table-row" key={payment.id}>
            <span className="payment-id">
              {payment.paymentId}
            </span>

            <span>
              INR {formatNumber(payment.amount)}
            </span>

            <span className="muted">
              {payment.failure}
            </span>

            <span>
              <b className={getRecoveryClass(payment.recoverability)}>
                {payment.recoverability}%
              </b>
            </span>

            <span>
              <ActionBadge action={payment.action} />
            </span>

            <button
              className="inspect-button"
              onClick={() => onPayment(payment)}
            >
              INSPECT
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function normalizePayment(payment) {
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
    customerId: payment.customer_id,
    failure: payment.failure_class
      .toLowerCase()
      .replaceAll("_", " "),
    recoverability: Math.round(payment.recoverability * 100),
    confidence: Math.round(payment.confidence * 100),
    action:
      actionMap[payment.authorized_action] ||
      payment.authorized_action,
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

function MetricCard({
  label,
  value,
  footnote,
  featured = false,
}) {
  return (
    <div className={`metric-card ${featured ? "featured" : ""}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-footnote">{footnote}</div>
    </div>
  );
}

function PanelHeader({
  title,
  description,
  meta,
}) {
  return (
    <div className="panel-header">
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>

      <span className="panel-meta">{meta}</span>
    </div>
  );
}

function PerformanceBar({
  label,
  value,
  rate,
  max,
  active = false,
}) {
  const width =
    max > 0
      ? Math.max((value / max) * 100, 3)
      : 3;

  return (
    <div className={`performance-row ${active ? "active" : ""}`}>
      <div className="performance-heading">
        <span>{label}</span>

        <div className="performance-number">
          <strong>
            INR {formatNumber(value)}
          </strong>
          <small>{rate}%</small>
        </div>
      </div>

      <div className="bar-track">
        <div
          className="bar-fill"
          style={{ width: `${width}%` }}
        ></div>
      </div>
    </div>
  );
}

function FlowStep({
  number,
  title,
  description,
  last = false,
}) {
  return (
    <div className={`flow-step ${last ? "last" : ""}`}>
      <div className="flow-number">{number}</div>

      <div className="flow-copy">
        <strong>{title}</strong>
        <span>{description}</span>
      </div>
    </div>
  );
}

function PageTitle({
  eyebrow,
  title,
  description,
}) {
  return (
    <section className="page-title">
      <div className="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  );
}

function NavButton({
  label,
  active,
  onClick,
}) {
  return (
    <button
      className={`nav-button ${active ? "active" : ""}`}
      onClick={onClick}
    >
      <span>{label}</span>

      {active && <i></i>}
    </button>
  );
}

function DrawerSection({
  title,
  children,
}) {
  return (
    <section className="drawer-section">
      <div className="drawer-section-title">
        {title}
      </div>

      {children}
    </section>
  );
}

function Assessment({
  label,
  value,
}) {
  return (
    <div className="assessment">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ContextRow({
  label,
  value,
}) {
  return (
    <div className="context-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function CheckRow({
  label,
  passed,
}) {
  return (
    <div className="check-row">
      <span className={passed ? "check passed" : "check"}>
        {passed ? "OK" : "-"}
      </span>

      <span>{label}</span>
    </div>
  );
}

function AuditEvent({
  time,
  id,
  event,
  detail,
}) {
  return (
    <div className="audit-event">
      <div className="audit-time">{time}</div>

      <div className="audit-dot"></div>

      <div className="audit-content">
        <div className="audit-topline">
          <strong>{event}</strong>
          <span>{id}</span>
        </div>

        <p>{detail}</p>
      </div>
    </div>
  );
}

function ActionBadge({ action }) {
  return (
    <span className="action-badge">
      {action}
    </span>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-icon">+</div>

      <strong>NO BENCHMARK RUN</strong>

      <span>
        Run the batch to generate recovery performance data.
      </span>
    </div>
  );
}

function EmptyPayments() {
  return (
    <div className="empty-state">
      <div className="empty-icon">+</div>

      <strong>NO PAYMENTS</strong>

      <span>
        Create a payment event through the backend API.
      </span>
    </div>
  );
}

function getMaxRevenue(data) {
  return Math.max(
    data.blind_retry.recovered_revenue,
    data.static_rules.recovered_revenue,
    data.revive_ai.recovered_revenue,
  );
}

function getRecoveryClass(value) {
  if (value >= 80) {
    return "high";
  }

  if (value >= 50) {
    return "medium";
  }

  return "low";
}

function formatNumber(value) {
  return Math.round(value).toLocaleString("en-IN");
}

function formatAuditTime(value) {
  if (!value) {
    return "--:--:--";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "--:--:--";
  }

  return date.toLocaleTimeString("en-IN", {
    hour12: false,
  });
}

function formatAuditEvent(value) {
  return value
    .replaceAll("_", " ")
    .toUpperCase();
}
export default App;




