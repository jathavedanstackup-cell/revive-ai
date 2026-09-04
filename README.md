# REVIVE AI

## AI-Powered Revenue Recovery Controller

REVIVE AI is a payment recovery decision system designed to determine the safest and most appropriate action after a payment failure.

Instead of blindly retrying every failed payment, REVIVE evaluates payment context, classifies the failure, estimates recoverability, and passes the recommendation through a deterministic policy gate before execution.

## Problem

Payment failures are not all the same. A transient issuer or network failure may be worth retrying. An insufficient-funds failure may require customer intervention. An uncertain failure may require escalation. A payment that has already been recovered should never be retried again.

## How REVIVE Works

Failed Payment
    |
    v
Context-Aware Diagnosis
    |
    v
Deterministic Policy Gate
    |
    v
Authorized Recovery Action
    |
    v
Bounded Executor
    |
    v
Payment State + Audit Trail

## Recovery Actions

- RETRY_NOW
- CUSTOMER_INTERVENTION
- ESCALATE
- STOP

## Safety Model

AI reasons. Policy authorizes.

Financial actions are bounded by retry limits, payment-state checks, confidence thresholds, recoverability thresholds, idempotency controls, and audit logging.

## Benchmark

REVIVE includes a deterministic payment simulation for reproducible evaluation.

The benchmark compares Blind Retry, Static Rules, and REVIVE AI using the same generated payment batch.

Metrics include recovered revenue, recovery rate, retry count, interventions, escalations, recovery cost, and net recovered revenue.

Benchmark results are simulation results and are not claims about production Razorpay performance.

## Product

- Revenue recovery overview
- Recovery strategy comparison
- Database-backed payment queue
- Payment investigation drawer
- Context-aware diagnosis
- Policy decision visibility
- Recovery execution
- Audit trail

## Architecture

React + Vite
|
v
FastAPI
|
+-- Payment APIs
+-- Diagnosis Engine
+-- Policy Engine
+-- Bounded Executor
+-- Audit API
+-- Simulation Engine
|
v
SQLite

External integration boundary:
Razorpay Adapter

## Razorpay Integration

REVIVE contains an isolated Razorpay provider adapter designed to connect the recovery domain to Razorpay APIs without coupling the core decision engine to the external provider.

The current prototype does not claim live Razorpay execution because merchant API credentials were not available during development.

The core simulation and recovery workflow operate independently of those credentials.

## Running Locally

### Backend

cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

Backend: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

### Frontend

cd frontend
npm install
npm run dev

Frontend: http://localhost:5173

## API

GET  /api/v1/health
POST /api/v1/payments/events
GET  /api/v1/payments
GET  /api/v1/payments/{payment_id}
POST /api/v1/recovery/analyze/{payment_id}
POST /api/v1/recovery/execute/{payment_id}
GET  /api/v1/audit
GET  /api/v1/analytics/benchmark
GET  /api/v1/analytics/summary
POST /api/v1/simulation/run

## Status

Functional prototype demonstrating payment failure ingestion, contextual diagnosis, deterministic policy authorization, bounded recovery execution, payment state transitions, idempotency protection, audit logging, reproducible benchmarking, and an interactive recovery control room.

## Disclaimer

REVIVE AI is a hackathon prototype and simulation environment. Benchmark results are generated from controlled synthetic scenarios and should not be interpreted as production payment performance.
