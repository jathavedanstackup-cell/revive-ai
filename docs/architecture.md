# REVIVE AI Architecture

## System Flow

Payment Failure
      |
      v
Payment Ingestion
      |
      v
Context-Aware Diagnosis
      |
      v
Recoverability + Confidence
      |
      v
Deterministic Policy Gate
      |
      v
Authorized Recovery Action
      |
      v
Bounded Recovery Executor
      |
      +----> Payment State
      |
      +----> Audit Trail
      |
      v
SQLite

External Integration Boundary
      |
      v
Razorpay Provider Adapter
