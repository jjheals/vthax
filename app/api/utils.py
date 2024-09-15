import pandas as pd 
import numpy as np
import networkx as nx


def df_to_graph(df:pd.DataFrame) -> nx.Graph: 
    """Takes in a dataframe with the index as the terrains and columns as vehicles, and the
    values as the edge weights, and constructs a graph to match this format."""

    # Init a new graph
    G:nx.Graph = nx.Graph()

    # Extract terrains and vehicles from the DataFrame
    terrains:list[str] = df.index.tolist()
    vehicles:list[str] = df.columns.tolist()

    # Add nodes for each terrain and vehicle
    G.add_nodes_from(terrains + vehicles)

    # Iterate through DataFrame to add edges with weights
    for terrain in terrains:
        for vehicle in vehicles:
            weight = df.at[terrain, vehicle]
            if weight != float('inf'):  # Skip invalid paths
                G.add_edge(terrain, vehicle, weight=weight)

    # Return the graph
    return G


def key_with_lowest_sum(d):
    min_sum = float('inf')  # Initialize to infinity
    min_key = None

    for key, subdict in d.items():
        # Calculate the sum of values in the sub-dictionary
        current_sum = sum(subdict.values())

        # Update min_key if the current_sum is lower than min_sum
        if current_sum < min_sum:
            min_sum = current_sum
            min_key = key

    return min_key