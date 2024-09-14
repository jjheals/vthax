import pandas as pd
import numpy as np
import json 


# Define terrain data
static_path_data = {
    "Path 1": {"Urban": 1, "Water": 2},
    "Path 2": {"Urban": 1, "Water": 2},
    "Path 3": {"Urban": 2, "Flatlands": 1},
    "Path 4": {"Urban": 1, "Flatlands": 1},
    "Path 5": {"Urban": 2, "Water": 1}
}

# Create DataFrame
terrain_df = pd.DataFrame(static_path_data).T.fillna(0)

# Define cost matrix
with open('costs.json', 'r') as file:
    costs = json.load(file)
    costs_matrix = pd.DataFrame(costs.values(), index=costs.keys())

# Function to calculate cost for a given path
def calculate_path_costs(terrain_counts, vehicle, costs_matrix):
    total_cost = 0
    for terrain, count in terrain_counts.items():
        if count <= 0: continue
        row = costs_matrix.loc[terrain]        
        cost = row.get(vehicle, -1)
        if cost == 'inf':
            return 'N/A'
        total_cost += cost * count

    return total_cost

# Calculate costs
vehicles = ['Helicopter', 'Boat', 'Car', 'Foot']
costs = {}

for path in terrain_df.index:
    costs[path] = {}
    terrain_counts = terrain_df.loc[path].to_dict()
    for vehicle in vehicles:
        costs[path][vehicle] = {}
        these_paths = calculate_path_costs(terrain_counts, vehicle, costs_matrix)
        costs[path][vehicle] = these_paths

# Convert costs to DataFrame for clarity
cost_df = pd.DataFrame(costs).T
print(cost_df)
