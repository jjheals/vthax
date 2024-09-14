import networkx as nx
import pandas as pd 
import numpy as np 

# ---- Setup/Init ---- #
# Define the graph
G = nx.Graph()

# Nodes representing terrain types
terrains:list[str] = ['Water', 'Forest', 'Flat Lands', 'Urban', 'Transport', 'Military']

# Vehicles
vehicles:list[str] = ['Helicopter', 'Boat', 'Car', 'Foot']


# ---- Generating Graph ---- # 
# Add nodes for each terrain
for terrain in terrains:
    G.add_node(terrain)

# Define the edge weights for each terrain/vehicle combination
weights:dict = {

    # WATER
    ('Water', 'Helicopter'): 1,
    ('Water', 'Boat'): 1,
    ('Water', 'Car'): float('inf'),
    ('Water', 'Foot'): float('inf'),
    
    # FOREST
    ('Forest', 'Helicopter'): 2,
    ('Forest', 'Boat'): float('inf'),
    ('Forest', 'Car'): float('inf'),
    ('Forest', 'Foot'): 7,

    # FLAT LANDS
    ('Flat Lands', 'Helicopter'): 1,
    ('Flat Lands', 'Boat'): float('inf'),
    ('Flat Lands', 'Car'): 5,
    ('Flat Lands', 'Foot'): 4,
    
    # URBAN 
    ('Urban', 'Helicopter'): 1,
    ('Urban', 'Boat'): float('inf'),
    ('Urban', 'Car'): 4,
    ('Urban', 'Foot'): 3,
    
    # TRANSPORT
    ('Loose Land', 'Helicopter'): 1,
    ('Loose Land', 'Boat'): float('inf'),
    ('Loose Land', 'Car'): 1,
    ('Loose Land', 'Foot'): 4,
    
    # MILITARY
    ('Mountainous', 'Helicopter'): 10,
    ('Mountainous', 'Boat'): float('inf'),
    ('Mountainous', 'Car'): 10,
    ('Mountainous', 'Foot'): 10
}

# Add edges to the graph
for (terrain, vehicle), weight in weights.items():
    if weight != float('inf'):  # Only add valid paths
        G.add_edge(terrain, vehicle, weight=weight)

# Initialize the matrix with infinity
matrix:np.matrix = np.full((len(terrains), len(vehicles)), float('inf'))

# Create a mapping from terrain and vehicle names to matrix indices
terrain_index:dict = {terrain: i for i, terrain in enumerate(terrains)}
vehicle_index:dict = {vehicle: j for j, vehicle in enumerate(vehicles)}

# Fill in the matrix with weights
for (terrain, vehicle), weight in weights.items():
    if weight != float('inf'):      # Skip invalid paths
        i = terrain_index[terrain]  # Row is the terrain 
        j = vehicle_index[vehicle]  # Column is the vehicle 
        matrix[i, j] = weight

# ---- Export ---- #
# Convert to DataFrame for exporting 
df = pd.DataFrame(matrix, index=terrains, columns=vehicles)
df.to_csv('terrain-vehicle-matrix.csv')

