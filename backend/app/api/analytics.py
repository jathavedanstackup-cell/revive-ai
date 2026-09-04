from fastapi import APIRouter

from simulation.benchmark import run_benchmark


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/benchmark")
def benchmark():
    return run_benchmark(count=1000, seed=42)


@router.get("/summary")
def summary():
    result = run_benchmark(count=1000, seed=42)

    revive = result["revive_ai"]
    blind = result["blind_retry"]
    static = result["static_rules"]

    return {
        "batch_size": result["batch_size"],
        "revive": revive,
        "comparison": {
            "blind_retry": blind,
            "static_rules": static,
        },
        "improvement_vs_static": round(
            revive["recovered_revenue"]
            - static["recovered_revenue"],
            2,
        ),
        "improvement_vs_blind": round(
            revive["recovered_revenue"]
            - blind["recovered_revenue"],
            2,
        ),
    }
