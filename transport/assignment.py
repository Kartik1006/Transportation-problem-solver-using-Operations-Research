import numpy as np
from .utils import create_step_log


def assignment_hungarian(costs):
    """
    Solve the assignment problem (Allocation special case: each supply=demand=1)
    using the Hungarian Algorithm. Returns steps and final assignment.

    Args:
        costs (array-like): m x n cost matrix. If m != n, the matrix is padded
                            with dummy rows/cols of zeros to make it square.

    Returns:
        dict: {
            'method': 'Hungarian Algorithm (Assignment)',
            'assignment': list of (i, j) pairs for original matrix indices,
            'total_cost': float total cost using original costs,
            'steps': list of step logs (including reduced matrices),
            'costs': original cost matrix as np.ndarray
        }
    """
    C_orig = np.array(costs, dtype=float)
    m, n = C_orig.shape
    steps = []

    # Pad to square matrix with dummy zeros (these represent dummy assignments)
    size = max(m, n)
    C = np.zeros((size, size))
    C[:m, :n] = C_orig

    step_num = 1
    steps.append(create_step_log(0, 'Initial matrix for Hungarian', costs=C.copy()))

    # Step 1: Row reduction
    row_mins = C.min(axis=1)
    C = (C.T - row_mins).T
    steps.append(create_step_log(step_num, f'Row reduction by {row_mins.tolist()}', costs=C.copy()))
    step_num += 1

    # Step 2: Column reduction
    col_mins = C.min(axis=0)
    C = C - col_mins
    steps.append(create_step_log(step_num, f'Column reduction by {col_mins.tolist()}', costs=C.copy()))
    step_num += 1

    def cover_zeros(matrix):
        """Cover all zeros using minimum number of lines. Returns row_cover, col_cover, num_lines."""
        n = matrix.shape[0]
        # Greedy heuristic: repeatedly cover the row/col with the most zeros
        mat = (matrix == 0).astype(int)
        row_cover = np.zeros(n, dtype=bool)
        col_cover = np.zeros(n, dtype=bool)
        while True:
            # Count uncovered zeros by row/col
            row_counts = np.where(~row_cover[:, None], mat, 0).sum(axis=1)
            col_counts = np.where(~col_cover[None, :], mat, 0).sum(axis=0)
            max_row = row_counts.max() if row_counts.size else 0
            max_col = col_counts.max() if col_counts.size else 0
            if max_row == 0 and max_col == 0:
                break
            if max_row >= max_col:
                r = int(np.argmax(row_counts))
                row_cover[r] = True
            else:
                c = int(np.argmax(col_counts))
                col_cover[c] = True
        num_lines = row_cover.sum() + col_cover.sum()
        return row_cover, col_cover, int(num_lines)

    def adjust_matrix(matrix, row_cover, col_cover):
        # Find minimum uncovered value
        mask = ~row_cover[:, None] & ~col_cover[None, :]
        if not np.any(mask):
            return matrix
        min_uncovered = matrix[mask].min()
        # Subtract from all uncovered, add to elements covered twice (rows and cols)
        matrix[mask] -= min_uncovered
        matrix[row_cover][:, col_cover] += min_uncovered
        return matrix

    def try_assignment(matrix):
        """Find a set of independent zeros (one per row/col) greedily."""
        n = matrix.shape[0]
        assigned_cols = set()
        assignment = [-1] * n
        # Strategy: prioritize rows with fewest zeros
        zero_positions = [(i, np.where(matrix[i] == 0)[0]) for i in range(n)]
        zero_positions.sort(key=lambda x: len(x[1]))
        for i, cols in zero_positions:
            for j in cols:
                if j not in assigned_cols:
                    assignment[i] = j
                    assigned_cols.add(j)
                    break
        if -1 in assignment:
            return None
        return assignment

    # Main loop: cover zeros and adjust until we can assign n zeros
    while True:
        row_cover, col_cover, num_lines = cover_zeros(C)
        steps.append(create_step_log(step_num, f'Cover zeros with {num_lines} line(s)', costs=C.copy()))
        step_num += 1

        if num_lines >= C.shape[0]:
            # Try to extract assignment
            assign = try_assignment(C)
            if assign is not None:
                break
            # Rare case: need another adjustment even though lines == n
        # Adjust matrix
        C = adjust_matrix(C, row_cover, col_cover)
        steps.append(create_step_log(step_num, 'Adjust matrix by smallest uncovered value', costs=C.copy()))
        step_num += 1

    # Build final assignment mapping back to original size
    assignment_pairs = []
    total_cost = 0.0
    for i, j in enumerate(assign):
        if i < m and j < n:
            assignment_pairs.append((i, j))
            total_cost += C_orig[i, j]
    
    return {
        'method': 'Hungarian Algorithm (Assignment)',
        'assignment': assignment_pairs,
        'total_cost': float(total_cost),
        'steps': steps,
        'costs': C_orig
    }

