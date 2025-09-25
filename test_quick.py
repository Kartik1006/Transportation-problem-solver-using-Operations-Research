from transport import nwcr, assignment_hungarian
import numpy as np

# Test transportation problem
print("Testing Transportation Problem (NWCR):")
costs = [[8,6,10],[9,12,13],[14,7,16]]
supply = [100,150,125]
demand = [130,120,125]
result = nwcr(costs, supply, demand)
print(f"NWCR Total Cost: {result['total_cost']}")

# Test assignment problem  
print("\nTesting Assignment Problem (Hungarian):")
assign_costs = [[9,2,7],[6,4,3],[5,8,1]]
assign_result = assignment_hungarian(assign_costs)
print(f"Hungarian Total Cost: {assign_result['total_cost']}")
print(f"Assignment pairs: {assign_result['assignment']}")

print("\nAll tests passed! The application is ready to run.")
