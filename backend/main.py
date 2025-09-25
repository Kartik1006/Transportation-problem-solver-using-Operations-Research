from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union, Optional, Dict, Any
import numpy as np

from transport import (
    nwcr, least_cost, vam, row_minima, assignment_hungarian, 
    modi_improvement, format_allocation_table
)

app = FastAPI(
    title="Transportation Problem Solver API",
    description="Solve transportation and assignment problems using various algorithms",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TransportationProblem(BaseModel):
    costs: List[List[float]]
    supply: List[float]
    demand: List[float]
    method: str  # "nwcr", "least_cost", "vam", "row_minima"
    use_modi: bool = False
    max_iterations: int = 10

class AssignmentProblem(BaseModel):
    costs: List[List[float]]

class SolutionResponse(BaseModel):
    method: str
    allocation: Optional[List[List[float]]] = None
    assignment: Optional[List[List[int]]] = None
    total_cost: float
    steps: List[Dict[str, Any]]
    costs: List[List[float]]
    supply: Optional[List[float]] = None
    demand: Optional[List[float]] = None
    dummy_added: Optional[Any] = None
    converged: Optional[bool] = None
    iterations: Optional[int] = None

def numpy_to_python(obj):
    """Convert numpy arrays to Python lists for JSON serialization"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [numpy_to_python(item) for item in obj]
    else:
        return obj

@app.get("/")
async def root():
    return {"message": "Transportation Problem Solver API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/solve/transportation", response_model=SolutionResponse)
async def solve_transportation_problem(problem: TransportationProblem):
    try:
        # Select method
        method_map = {
            "nwcr": nwcr,
            "least_cost": least_cost,
            "vam": vam,
            "row_minima": row_minima
        }
        
        if problem.method not in method_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid method. Choose from: {list(method_map.keys())}"
            )
        
        method_func = method_map[problem.method]
        
        # Solve initial problem
        result = method_func(problem.costs, problem.supply, problem.demand)
        
        # Apply MODI if requested
        if problem.use_modi:
            modi_result = modi_improvement(
                result['allocation'], 
                result['costs'], 
                problem.max_iterations
            )
            # Merge results
            result.update({
                'total_cost': modi_result['total_cost'],
                'allocation': modi_result['allocation'],
                'converged': modi_result.get('converged'),
                'iterations': modi_result.get('iterations'),
                'steps': result['steps'] + modi_result['steps']
            })
        
        # Convert numpy arrays to Python lists
        result = numpy_to_python(result)
        
        return SolutionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve/assignment", response_model=SolutionResponse)
async def solve_assignment_problem(problem: AssignmentProblem):
    try:
        result = assignment_hungarian(problem.costs)
        result = numpy_to_python(result)
        return SolutionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize/modi")
async def optimize_with_modi(
    allocation: List[List[float]], 
    costs: List[List[float]], 
    max_iterations: int = 10
):
    try:
        result = modi_improvement(allocation, costs, max_iterations)
        result = numpy_to_python(result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/methods")
async def get_available_methods():
    return {
        "transportation_methods": [
            {"key": "nwcr", "name": "North-West Corner Rule (NWCR)"},
            {"key": "least_cost", "name": "Least Cost Method"},
            {"key": "vam", "name": "Vogel's Approximation Method (VAM)"},
            {"key": "row_minima", "name": "Row Minima (Special Case)"}
        ],
        "assignment_methods": [
            {"key": "hungarian", "name": "Hungarian Algorithm"}
        ],
        "optimization_methods": [
            {"key": "modi", "name": "MODI (Modified Distribution)"}
        ]
    }

@app.post("/validate/transportation")
async def validate_transportation_input(problem: TransportationProblem):
    try:
        costs = np.array(problem.costs)
        supply = np.array(problem.supply)
        demand = np.array(problem.demand)
        
        if costs.shape[0] != len(supply):
            raise ValueError("Cost matrix rows must match supply length")
        
        if costs.shape[1] != len(demand):
            raise ValueError("Cost matrix columns must match demand length")
        
        total_supply = np.sum(supply)
        total_demand = np.sum(demand)
        
        return {
            "valid": True,
            "total_supply": float(total_supply),
            "total_demand": float(total_demand),
            "balanced": abs(total_supply - total_demand) < 1e-6,
            "matrix_size": list(costs.shape)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

@app.post("/validate/assignment")
async def validate_assignment_input(problem: AssignmentProblem):
    try:
        costs = np.array(problem.costs)
        
        if costs.shape[0] != costs.shape[1]:
            raise ValueError("Assignment problem requires square cost matrix")
        
        return {
            "valid": True,
            "matrix_size": list(costs.shape)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
