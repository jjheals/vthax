import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load terrain data
with open('tmp.json', 'r') as f:
    data = json.load(f)

# Extract and reformat the terrain counts
static_path_data = {}
for path, details in data.items():
    terrain_counts = details['terrain_counts']
    
    # Capitalize the first letter of each terrain type
    formatted_terrain = {terrain.capitalize(): count for terrain, count in terrain_counts.items()}
    
    static_path_data[path] = formatted_terrain

# Create DataFrame for terrain data
terrain_df = pd.DataFrame(static_path_data).T.fillna(0)

# Load cost matrix
with open('costs.json', 'r') as file:
    costs = json.load(file)

# Convert all values in costs_matrix to numeric, replacing 'inf' with np.inf
costs_matrix = pd.DataFrame(costs).applymap(lambda x: np.inf if x == "inf" else pd.to_numeric(x, errors='coerce'))

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

# Calculate costs
vehicles = ['Helicopter', 'Boat', 'Car', 'Foot']
cost_df = pd.DataFrame({
    vehicle: [
        calculate_path_costs(terrain_df.loc[path].to_dict(), vehicle, costs_matrix)
        for path in terrain_df.index
    ]
    for vehicle in vehicles
}, index=terrain_df.index)

# Replace NaNs (which represent infinite costs) with a large value (e.g., 1000)
cost_df.replace(np.nan, 1000, inplace=True)

# Combine terrain data and cost data into a single DataFrame
df_paths = terrain_df.join(cost_df)

# Print the cleaned DataFrame
print("Cleaned DataFrame:")
print(df_paths)

# Replace NaNs with zero for machine learning model (you can also leave them as they are if that's part of your logic)
df_paths.fillna(0, inplace=True)

# Create a dummy label column for the sake of this example
df_paths['label'] = np.random.choice([0, 1], size=len(df_paths))  # Example label

# Split data into features and labels
X = df_paths.drop('label', axis=1)
y = df_paths['label']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train a Random Forest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.2f}")
print("Predictions on test set:")
print(y_pred)
