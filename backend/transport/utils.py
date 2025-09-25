import numpy as np
import pandas as pd


def validate_input(costs, supply, demand):
    """Validate that inputs have consistent dimensions and are positive."""
    costs = np.array(costs, dtype=float)
    supply = np.array(supply, dtype=float)
    demand = np.array(demand, dtype=float)
    
    if costs.shape[0] != len(supply):
        raise ValueError(f"Cost matrix rows ({costs.shape[0]}) must match supply length ({len(supply)})")
    
    if costs.shape[1] != len(demand):
        raise ValueError(f"Cost matrix columns ({costs.shape[1]}) must match demand length ({len(demand)})")
    
    if np.any(costs < 0):
        raise ValueError("All costs must be non-negative")
    
    if np.any(supply < 0):
        raise ValueError("All supply values must be non-negative")
    
    if np.any(demand < 0):
        raise ValueError("All demand values must be non-negative")
    
    return costs, supply, demand


def balance_problem(costs, supply, demand):
    """Balance supply and demand by adding dummy sources/destinations."""
    costs = np.array(costs, dtype=float)
    supply = np.array(supply, dtype=float)
    demand = np.array(demand, dtype=float)
    
    total_supply = np.sum(supply)
    total_demand = np.sum(demand)
    
    # Track original dimensions for later interpretation
    original_m, original_n = costs.shape
    dummy_added = False
    
    if total_supply > total_demand:
        # Add dummy destination
        dummy_demand = total_supply - total_demand
        demand = np.append(demand, dummy_demand)
        # Add column of zeros for dummy destination costs
        dummy_column = np.zeros((costs.shape[0], 1))
        costs = np.hstack([costs, dummy_column])
        dummy_added = ("destination", dummy_demand)
        
    elif total_demand > total_supply:
        # Add dummy source
        dummy_supply = total_demand - total_supply
        supply = np.append(supply, dummy_supply)
        # Add row of zeros for dummy source costs  
        dummy_row = np.zeros((1, costs.shape[1]))
        costs = np.vstack([costs, dummy_row])
        dummy_added = ("source", dummy_supply)
    
    return costs, supply, demand, dummy_added


def calculate_total_cost(allocation, costs):
    """Calculate the total transportation cost."""
    return np.sum(allocation * costs)


def create_step_log(step_number, description, allocation=None, costs=None, supply=None, demand=None):
    """Create a formatted step log entry."""
    step_info = {
        'step': step_number,
        'description': description
    }
    
    if allocation is not None:
        step_info['allocation'] = allocation.copy()
    if costs is not None:
        step_info['costs'] = costs.copy()
    if supply is not None:
        step_info['remaining_supply'] = supply.copy()
    if demand is not None:
        step_info['remaining_demand'] = demand.copy()
    
    return step_info


def format_allocation_table(allocation, costs, row_names=None, col_names=None):
    """Format allocation matrix as a readable table."""
    m, n = allocation.shape
    
    if row_names is None:
        row_names = [f"S{i+1}" for i in range(m)]
    if col_names is None:
        col_names = [f"D{j+1}" for j in range(n)]
    
    # Create display data combining allocation and costs
    display_data = []
    for i in range(m):
        row_data = []
        for j in range(n):
            if allocation[i, j] > 0:
                cell = f"{allocation[i, j]:.0f} ({costs[i, j]:.1f})"
            else:
                cell = f"- ({costs[i, j]:.1f})"
            row_data.append(cell)
        display_data.append(row_data)
    
    df = pd.DataFrame(display_data, index=row_names, columns=col_names)
    return df


def get_basic_variables(allocation):
    """Get indices of basic variables (non-zero allocations)."""
    return [(i, j) for i in range(allocation.shape[0]) 
            for j in range(allocation.shape[1]) 
            if allocation[i, j] > 0]


def is_degenerate(allocation):
    """Check if the solution is degenerate."""
    m, n = allocation.shape
    basic_vars = len(get_basic_variables(allocation))
    expected_vars = m + n - 1
    return basic_vars < expected_vars


def add_epsilon_allocation(allocation, costs):
    """Add small epsilon allocation to handle degeneracy."""
    allocation = allocation.copy()
    epsilon = 1e-10
    
    # Find the minimum cost cell that's currently zero
    min_cost = float('inf')
    min_pos = None
    
    for i in range(allocation.shape[0]):
        for j in range(allocation.shape[1]):
            if allocation[i, j] == 0 and costs[i, j] < min_cost:
                min_cost = costs[i, j]
                min_pos = (i, j)
    
    if min_pos:
        allocation[min_pos] = epsilon
    
    return allocation
