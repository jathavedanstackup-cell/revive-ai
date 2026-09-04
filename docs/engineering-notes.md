# Engineering Notes

## Frontend Recovery-State Synchronization

### Problem

After a successful recovery execution, the backend correctly changed the payment state from FAILED to RECOVERED, but the selected payment shown in the frontend investigation drawer still displayed the previous state.

### Cause

The React selected-payment state was not immediately synchronized with the recovery execution response.

### Fix

The frontend now updates the selected payment after a successful execution and reloads the database-backed payment queue.

### Result

The complete state transition is now visible:

FAILED
    |
    v
RETRY_NOW
    |
    v
SUCCESS
    |
    v
RECOVERED
    |
    v
STOP

## Razorpay Integration Limitation

A Razorpay merchant API credential set was not available during development. The project therefore does not claim live Razorpay API execution was validated.

Instead, REVIVE uses a controlled simulation for the complete recovery workflow and keeps the Razorpay integration isolated behind a provider adapter boundary.

## Benchmark Reproducibility

The benchmark uses a fixed seed and the same generated payment batch for each strategy.

The benchmark was executed twice with:

count = 1000
seed = 42

Both runs produced identical results.

## Engineering Principle

AI is used for contextual diagnosis and recommendation. Deterministic policy logic controls financial authorization, retry limits, payment-state checks, and stopping behavior.
