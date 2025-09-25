import numpy as np
from .utils import create_step_log, get_basic_variables, is_degenerate, add_epsilon_allocation


def modi_improvement(allocation, costs, max_iterations=10):
    """
    Apply MODI (Modified Distribution) method to improve a basic feasible solution.
    
    Args:
        allocation: Initial allocation matrix (basic feasible solution)
        costs: Cost matrix
        max_iterations: Maximum number of iterations to perform
        
    Returns:
        dict: Contains improved allocation, total cost, and step-by-step logs
    """
    allocation = np.array(allocation, dtype=float)
    costs = np.array(costs, dtype=float)
    m, n = costs.shape
    
    steps = []
    step_num = 1
    iteration = 0
    
    # Initial step
    initial_cost = np.sum(allocation * costs)
    steps.append(create_step_log(0, f"Initial solution with cost {initial_cost}", 
                                allocation, costs))
    
    while iteration < max_iterations:
        iteration += 1
        
        # Handle degeneracy if needed
        if is_degenerate(allocation):
            allocation = add_epsilon_allocation(allocation, costs)
            steps.append(create_step_log(step_num, "Added epsilon allocation to handle degeneracy", 
                                        allocation, costs))
            step_num += 1
        
        # Get basic variables (non-zero allocations)
        basic_vars = get_basic_variables(allocation)
        
        # Step 1: Calculate ui and vj values
        ui = np.full(m, np.nan)
        vj = np.full(n, np.nan)
        
        # Set u0 = 0 (arbitrary choice)
        ui[0] = 0
        
        # Iteratively solve ui + vj = cij for basic variables
        changed = True
        while changed:
            changed = False
            for i, j in basic_vars:
                if not np.isnan(ui[i]) and np.isnan(vj[j]):
                    vj[j] = costs[i, j] - ui[i]
                    changed = True
                elif np.isnan(ui[i]) and not np.isnan(vj[j]):
                    ui[i] = costs[i, j] - vj[j]
                    changed = True
        
        # Check if all ui and vj are computed
        if np.any(np.isnan(ui)) or np.any(np.isnan(vj)):
            steps.append(create_step_log(step_num, "Could not compute all ui and vj values - solution may be degenerate", 
                                        allocation, costs))
            break
        
        ui_str = ", ".join([f"u{i+1}={ui[i]:.2f}" for i in range(m)])
        vj_str = ", ".join([f"v{j+1}={vj[j]:.2f}" for j in range(n)])
        steps.append(create_step_log(step_num, f"Computed potentials: {ui_str}, {vj_str}", 
                                    allocation, costs))
        step_num += 1
        
        # Step 2: Calculate opportunity costs (dij = cij - ui - vj)
        opportunity_costs = costs - ui[:, np.newaxis] - vj[np.newaxis, :]
        
        # Find the most negative opportunity cost (for maximization, or most positive for minimization)
        min_opportunity = np.min(opportunity_costs)
        
        if min_opportunity >= -1e-10:  # Solution is optimal (within tolerance)
            steps.append(create_step_log(step_num, f"Optimal solution found! All opportunity costs ≥ 0. Min = {min_opportunity:.6f}", 
                                        allocation, costs))
            break
        
        # Find entering variable (most negative opportunity cost)
        entering_pos = np.unravel_index(np.argmin(opportunity_costs), opportunity_costs.shape)
        entering_i, entering_j = entering_pos
        
        opp_cost_str = f"Most negative opportunity cost: d_{entering_i+1}{entering_j+1} = {min_opportunity:.3f}"
        steps.append(create_step_log(step_num, opp_cost_str, allocation, costs))
        step_num += 1
        
        # Step 3: Find loop and determine leaving variable
        loop_result = find_loop(allocation, entering_i, entering_j)
        if loop_result is None:
            steps.append(create_step_log(step_num, "Could not find closed loop - stopping", 
                                        allocation, costs))
            break
        
        loop_path, theta = loop_result
        
        # Describe the loop
        loop_str = " → ".join([f"({i+1},{j+1})" for i, j in loop_path])
        steps.append(create_step_log(step_num, f"Found loop: {loop_str}, θ = {theta}", 
                                    allocation, costs))
        step_num += 1
        
        # Step 4: Update allocation
        for idx, (i, j) in enumerate(loop_path):
            if idx % 2 == 0:  # Add theta
                allocation[i, j] += theta
            else:  # Subtract theta
                allocation[i, j] -= theta
        
        new_cost = np.sum(allocation * costs)
        cost_improvement = initial_cost - new_cost
        steps.append(create_step_log(step_num, f"Updated allocation. New cost: {new_cost}, Improvement: {cost_improvement:.3f}", 
                                    allocation, costs))
        step_num += 1
        
        # Clean up very small values (numerical precision)
        allocation[allocation < 1e-10] = 0
    
    final_cost = np.sum(allocation * costs)
    
    return {
        'method': 'MODI (Modified Distribution)',
        'allocation': allocation,
        'total_cost': final_cost,
        'steps': steps,
        'costs': costs,
        'iterations': iteration,
        'converged': min_opportunity >= -1e-10 if 'min_opportunity' in locals() else False
    }


def find_loop(allocation, entering_i, entering_j):
    """
    Find a closed loop starting from the entering variable position.
    Returns the loop path and theta (maximum amount that can be reallocated).
    """
    m, n = allocation.shape
    basic_vars = get_basic_variables(allocation)
    
    # Build adjacency information
    # For each row, find which columns have basic variables
    row_cols = {}
    for i in range(m):
        row_cols[i] = [j for i2, j in basic_vars if i2 == i]
    
    # For each column, find which rows have basic variables  
    col_rows = {}
    for j in range(n):
        col_rows[j] = [i for i, j2 in basic_vars if j2 == j]
    
    def dfs_loop(path, visited_positions):
        """Depth-first search to find a closed loop."""
        if len(path) < 4:  # Need at least 4 positions for a loop
            current_i, current_j = path[-1]
            
            if len(path) % 2 == 1:  # Odd length - move horizontally
                # Try other columns in this row
                for next_j in row_cols.get(current_i, []):
                    if (current_i, next_j) not in visited_positions:
                        new_path = path + [(current_i, next_j)]
                        new_visited = visited_positions | {(current_i, next_j)}
                        result = dfs_loop(new_path, new_visited)
                        if result:
                            return result
            else:  # Even length - move vertically
                # Try other rows in this column
                for next_i in col_rows.get(current_j, []):
                    if (next_i, current_j) not in visited_positions:
                        new_path = path + [(next_i, current_j)]
                        new_visited = visited_positions | {(next_i, current_j)}
                        result = dfs_loop(new_path, new_visited)
                        if result:
                            return result
        
        # Check if we can close the loop
        if len(path) >= 4:
            current_i, current_j = path[-1]
            start_i, start_j = path[0]
            
            if len(path) % 2 == 0:  # Even length - should be able to move vertically to start
                if start_j == current_j and start_i != current_i:
                    return path  # Found a loop!
            else:  # Odd length - should be able to move horizontally to start  
                if start_i == current_i and start_j != current_j:
                    return path  # Found a loop!
        
        return None
    
    # Start DFS from entering position, trying both horizontal and vertical first moves
    start_path = [(entering_i, entering_j)]
    start_visited = {(entering_i, entering_j)}
    
    # Try moving horizontally first
    for next_j in row_cols.get(entering_i, []):
        if (entering_i, next_j) not in start_visited:
            path = start_path + [(entering_i, next_j)]
            visited = start_visited | {(entering_i, next_j)}
            loop = dfs_loop(path, visited)
            if loop:
                # Calculate theta (minimum allocation in positions to be decreased)
                theta = float('inf')
                for idx in range(1, len(loop), 2):  # Odd indices will be decreased
                    i, j = loop[idx]
                    theta = min(theta, allocation[i, j])
                return loop, theta
    
    # Try moving vertically first
    for next_i in col_rows.get(entering_j, []):
        if (next_i, entering_j) not in start_visited:
            path = start_path + [(next_i, entering_j)]
            visited = start_visited | {(next_i, entering_j)}
            loop = dfs_loop(path, visited)
            if loop:
                # Calculate theta
                theta = float('inf')
                for idx in range(1, len(loop), 2):  # Odd indices will be decreased
                    i, j = loop[idx]
                    theta = min(theta, allocation[i, j])
                return loop, theta
    
    return None
