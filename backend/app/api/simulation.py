from fastapi import APIRouter
from pydantic import BaseModel

from simulation.benchmark import run_benchmark


router = APIRouter(prefix="/simulation", tags=["Simulation"])


class SimulationRequest(BaseModel):
    count: int = 1000
    seed: int = 42


@router.post("/run")
def run_simulation(request: SimulationRequest):
    return run_benchmark(
        count=request.count,
        seed=request.seed,
    )
