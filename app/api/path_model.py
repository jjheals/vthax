import pandas as pd
import numpy as np
import json

def get_top_5_combinations(terrain_data, cost_matrix, vehicles):
    # Extract and reformat the terrain counts
    static_path_data = {}
    for path, details in terrain_data.items():
        terrain_counts = details['terrain_counts']
        
        # Capitalize the first letter of each terrain type
        formatted_terrain = {terrain.capitalize(): count for terrain, count in terrain_counts.items()}
        
        static_path_data[path] = formatted_terrain

    # Create DataFrame for terrain data
    terrain_df = pd.DataFrame(static_path_data).T.fillna(0)

    # Convert all values in costs_matrix to numeric, replacing 'inf' with np.inf
    costs_matrix = pd.DataFrame(cost_matrix).applymap(lambda x: np.inf if x == "inf" else pd.to_numeric(x, errors='coerce'))

    # Transpose the costs_matrix if needed to align terrain types with index
    if set(costs_matrix.columns).intersection(terrain_df.columns):
        costs_matrix = costs_matrix.T

    # Check alignment between terrain types
    common_terrains = terrain_df.columns.intersection(costs_matrix.index)

    # Subset both DataFrames to the common terrain types
    terrain_df = terrain_df[common_terrains]
    costs_matrix = costs_matrix.loc[common_terrains]

    # Function to calculate cost for a given path
    def calculate_path_costs(terrain_counts, vehicle, costs_matrix):
        total_cost = 0
        for terrain, count in terrain_counts.items():
            if count > 0:
                if terrain in costs_matrix.index:
                    cost = costs_matrix.at[terrain, vehicle]
                    if pd.notna(cost):
                        total_cost += cost * count
                    else:
                        total_cost += np.inf  # Impossible route, so set to infinity
        return total_cost if total_cost != np.inf else np.nan

    # Calculate costs for each vehicle
    all_costs = []
    for vehicle in vehicles:
        costs_for_vehicle = [
            (path, vehicle, calculate_path_costs(terrain_df.loc[path].to_dict(), vehicle, costs_matrix))
            for path in terrain_df.index
        ]
        all_costs.extend(costs_for_vehicle)

    # Convert to DataFrame and sort by cost
    cost_df = pd.DataFrame(all_costs, columns=['Path', 'Vehicle', 'Cost'])
    cost_df = cost_df.sort_values(by='Cost')

    # Get top 5 path/vehicle combinations
    top_5_combos = cost_df.head(5)

    # Format output for top 5 combos
    top_5_dict = {}
    for _, row in top_5_combos.iterrows():
        path = row['Path']
        vehicle = row['Vehicle']
        cost = row['Cost']
        if path not in top_5_dict:
            top_5_dict[path] = {}
        top_5_dict[path][vehicle] = cost

    return top_5_dict

