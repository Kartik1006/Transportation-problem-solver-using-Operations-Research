import numpy as np
from .utils import validate_input, balance_problem, calculate_total_cost, create_step_log


def nwcr(costs, supply, demand):
    """
    North-West Corner Rule (NWCR) method for initial solution.
    
    Returns:
        dict: Contains final allocation, total cost, and step-by-step logs
    """
    costs, supply, demand = validate_input(costs, supply, demand)
    costs, supply, demand, dummy_added = balance_problem(costs, supply, demand)
    
    m, n = costs.shape
    allocation = np.zeros((m, n))
    remaining_supply = supply.copy()
    remaining_demand = demand.copy()
    
    steps = []
    step_num = 1
    
    # Initial step
    steps.append(create_step_log(0, "Initial problem setup", 
                                allocation, costs, remaining_supply, remaining_demand))
    
    i, j = 0, 0
    
    while i < m and j < n:
        # Allocate minimum of remaining supply and demand
        allocation_amount = min(remaining_supply[i], remaining_demand[j])
        allocation[i, j] = allocation_amount
        
        remaining_supply[i] -= allocation_amount
        remaining_demand[j] -= allocation_amount
        
        description = f"Allocate {allocation_amount} to cell ({i+1}, {j+1})"
        steps.append(create_step_log(step_num, description, 
                                    allocation, costs, remaining_supply, remaining_demand))
        step_num += 1
        
        # Move to next cell: if supply exhausted, move down; if demand exhausted, move right
        if remaining_supply[i] == 0:
            i += 1
        if remaining_demand[j] == 0:
            j += 1
    
    total_cost = calculate_total_cost(allocation, costs)
    
    return {
        'method': 'North-West Corner Rule (NWCR)',
        'allocation': allocation,
        'total_cost': total_cost,
        'steps': steps,
        'costs': costs,
        'supply': supply,
        'demand': demand,
        'dummy_added': dummy_added
    }


def least_cost(costs, supply, demand):
    """
    Least Cost Method for initial solution.
    
    Returns:
        dict: Contains final allocation, total cost, and step-by-step logs
    """
    costs, supply, demand = validate_input(costs, supply, demand)
    costs, supply, demand, dummy_added = balance_problem(costs, supply, demand)
    
    m, n = costs.shape
    allocation = np.zeros((m, n))
    remaining_supply = supply.copy()
    remaining_demand = demand.copy()
    
    steps = []
    step_num = 1
    
    # Initial step
    steps.append(create_step_log(0, "Initial problem setup", 
                                allocation, costs, remaining_supply, remaining_demand))
    
    # Create availability mask for cells
    available = np.ones((m, n), dtype=bool)
    
    while np.sum(remaining_supply) > 1e-10 and np.sum(remaining_demand) > 1e-10:
        # Find minimum cost among available cells
        available_costs = np.where(available, costs, np.inf)
        min_cost_idx = np.unravel_index(np.argmin(available_costs), costs.shape)
        i, j = min_cost_idx
        
        # Allocate minimum of remaining supply and demand
        allocation_amount = min(remaining_supply[i], remaining_demand[j])
        allocation[i, j] = allocation_amount
        
        remaining_supply[i] -= allocation_amount
        remaining_demand[j] -= allocation_amount
        
        description = f"Allocate {allocation_amount} to cell ({i+1}, {j+1}) with cost {costs[i, j]}"
        steps.append(create_step_log(step_num, description, 
                                    allocation, costs, remaining_supply, remaining_demand))
        step_num += 1
        
        # Update availability
        if remaining_supply[i] == 0:
            available[i, :] = False
        if remaining_demand[j] == 0:
            available[:, j] = False
    
    total_cost = calculate_total_cost(allocation, costs)
    
    return {
        'method': 'Least Cost Method',
        'allocation': allocation,
        'total_cost': total_cost,
        'steps': steps,
        'costs': costs,
        'supply': supply,
        'demand': demand,
        'dummy_added': dummy_added
    }


def vam(costs, supply, demand):
    """
    Vogel's Approximation Method (VAM) for initial solution.
    
    Returns:
        dict: Contains final allocation, total cost, and step-by-step logs
    """
    costs, supply, demand = validate_input(costs, supply, demand)
    costs, supply, demand, dummy_added = balance_problem(costs, supply, demand)
    
    m, n = costs.shape
    allocation = np.zeros((m, n))
    remaining_supply = supply.copy()
    remaining_demand = demand.copy()
    
    steps = []
    step_num = 1
    
    # Initial step
    steps.append(create_step_log(0, "Initial problem setup", 
                                allocation, costs, remaining_supply, remaining_demand))
    
    # Track active rows and columns
    active_rows = list(range(m))
    active_cols = list(range(n))
    
    while len(active_rows) > 0 and len(active_cols) > 0:
        # Calculate penalties for active rows
        row_penalties = []
        row_penalty_info = []
        for i in active_rows:
            if len(active_cols) >= 2:
                row_costs = [costs[i, j] for j in active_cols]
                row_costs.sort()
                penalty = row_costs[1] - row_costs[0]
            else:
                penalty = 0
            row_penalties.append(penalty)
            row_penalty_info.append(f"Row {i+1}: {penalty}")
        
        # Calculate penalties for active columns
        col_penalties = []
        col_penalty_info = []
        for j in active_cols:
            if len(active_rows) >= 2:
                col_costs = [costs[i, j] for i in active_rows]
                col_costs.sort()
                penalty = col_costs[1] - col_costs[0]
            else:
                penalty = 0
            col_penalties.append(penalty)
            col_penalty_info.append(f"Col {j+1}: {penalty}")
        
        # Find maximum penalty
        max_row_penalty = max(row_penalties) if row_penalties else -1
        max_col_penalty = max(col_penalties) if col_penalties else -1
        
        penalty_description = f"Penalties - {', '.join(row_penalty_info)}, {', '.join(col_penalty_info)}"
        
        if max_row_penalty >= max_col_penalty:
            # Select row with maximum penalty
            selected_row_idx = row_penalties.index(max_row_penalty)
            i = active_rows[selected_row_idx]
            
            # Find minimum cost in this row among active columns
            min_cost = min(costs[i, j] for j in active_cols)
            j = next(j for j in active_cols if costs[i, j] == min_cost)
            
            selected_info = f"Selected row {i+1} (penalty {max_row_penalty}), min cost cell ({i+1}, {j+1})"
        else:
            # Select column with maximum penalty
            selected_col_idx = col_penalties.index(max_col_penalty)
            j = active_cols[selected_col_idx]
            
            # Find minimum cost in this column among active rows
            min_cost = min(costs[i, j] for i in active_rows)
            i = next(i for i in active_rows if costs[i, j] == min_cost)
            
            selected_info = f"Selected col {j+1} (penalty {max_col_penalty}), min cost cell ({i+1}, {j+1})"
        
        # Allocate
        allocation_amount = min(remaining_supply[i], remaining_demand[j])
        allocation[i, j] = allocation_amount
        
        remaining_supply[i] -= allocation_amount
        remaining_demand[j] -= allocation_amount
        
        description = f"{penalty_description}. {selected_info}. Allocate {allocation_amount}"
        steps.append(create_step_log(step_num, description, 
                                    allocation, costs, remaining_supply, remaining_demand))
        step_num += 1
        
        # Remove exhausted rows/columns
        if remaining_supply[i] == 0 and i in active_rows:
            active_rows.remove(i)
        if remaining_demand[j] == 0 and j in active_cols:
            active_cols.remove(j)
    
    total_cost = calculate_total_cost(allocation, costs)
    
    return {
        'method': "Vogel's Approximation Method (VAM)",
        'allocation': allocation,
        'total_cost': total_cost,
        'steps': steps,
        'costs': costs,
        'supply': supply,
        'demand': demand,
        'dummy_added': dummy_added
    }


def row_minima(costs, supply, demand):
    """
    Row Minima Method (as a special case allocation heuristic).
    Allocates to minimum cost cell in each row sequentially.
    
    Returns:
        dict: Contains final allocation, total cost, and step-by-step logs
    """
    costs, supply, demand = validate_input(costs, supply, demand)
    costs, supply, demand, dummy_added = balance_problem(costs, supply, demand)
    
    m, n = costs.shape
    allocation = np.zeros((m, n))
    remaining_supply = supply.copy()
    remaining_demand = demand.copy()
    
    steps = []
    step_num = 1
    
    # Initial step
    steps.append(create_step_log(0, "Initial problem setup", 
                                allocation, costs, remaining_supply, remaining_demand))
    
    for i in range(m):
        while remaining_supply[i] > 1e-10:
            # Find available columns (with remaining demand)
            available_cols = [j for j in range(n) if remaining_demand[j] > 1e-10]
            
            if not available_cols:
                break
                
            # Find minimum cost among available columns in this row
            min_cost = min(costs[i, j] for j in available_cols)
            j = next(j for j in available_cols if costs[i, j] == min_cost)
            
            # Allocate
            allocation_amount = min(remaining_supply[i], remaining_demand[j])
            allocation[i, j] = allocation_amount
            
            remaining_supply[i] -= allocation_amount
            remaining_demand[j] -= allocation_amount
            
            description = f"Row {i+1}: Allocate {allocation_amount} to min cost cell ({i+1}, {j+1}) with cost {costs[i, j]}"
            steps.append(create_step_log(step_num, description, 
                                        allocation, costs, remaining_supply, remaining_demand))
            step_num += 1
    
    total_cost = calculate_total_cost(allocation, costs)
    
    return {
        'method': 'Row Minima (Special Case)',
        'allocation': allocation,
        'total_cost': total_cost,
        'steps': steps,
        'costs': costs,
        'supply': supply,
        'demand': demand,
        'dummy_added': dummy_added
    }
