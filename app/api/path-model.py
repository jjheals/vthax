import pandas as pd
import numpy as np
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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

# Convert all values in costs_matrix to numeric, replacing errors with NaN
costs_matrix = costs_matrix.apply(pd.to_numeric, errors='coerce')

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
                    total_cost += float('inf')  
    return total_cost if total_cost != float('inf') else np.nan

# Calculate costs
vehicles = ['Helicopter', 'Boat', 'Car', 'Foot']
cost_df = pd.DataFrame({
    vehicle: [
        calculate_path_costs(terrain_df.loc[path].to_dict(), vehicle, costs_matrix)
        for path in terrain_df.index
    ]
    for vehicle in vehicles
}, index=terrain_df.index)

print("Cost DataFrame:")
print(cost_df)

# Combine terrain data and cost data into a single DataFrame
df_paths = terrain_df.join(cost_df)

print("\nCombined DataFrame:")
print(df_paths)

# Replace NaNs with zero for machine learning model
df_paths.fillna(0, inplace=True)

# Print cleaned DataFrame
print("After cleaning:")
print(df_paths.describe())
print(df_paths.head())

# Create a dummy label column for the sake of this example
# Replace with your actual label column or target variable
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
