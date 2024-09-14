from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS 
from geopy.distance import geodesic
import requests
import numpy as np
import pandas as pd
from collections import Counter
# from utils import df_to_graph

# ---- Init flask ---- #
app = Flask(__name__)
compress = Compress()
compress.init_app(app)

# Init CORS with the URL of the React app
CORS(app, origins=['http://localhost:3000'])  

# ---- Init backend ---- #
# Load the data, graph, etc. 
# vehicles_df:pd.DataFrame = pd.read_csv('../../data/static/vehicle-definitions.csv')
# terrain_df:pd.DataFrame = pd.read_csv('../../data/static/terrain-definitions.csv')
# terrain_vehicle_matrix:np.matrix = df_to_graph(pd.read_csv('../../data/static/terrain-vehicle-matrix.csv'))

# ---- ENDPOINTS ---- #
@app.route('/get-input-params', methods=['GET'])
def get_input_params(): 
    """ Returns the data displayed in the sidebar of inputs that need to be supplied
    by the user, as well as bounds, types, etc. as applicable."""

    data:dict = {
        'vehicles': [
            {
                'vehicle-id': r['vehicle_id'],
                'vehicle-name': r['vehicle_name'],
                'vehicle-description': r['description']
            } for idx, r in vehicles_df.iterrows()
        ]
    }

    return jsonify(
        { 'data': data }
    )


@app.route('/elevation', methods=['GET'])
def get_elevation():
    start_lat = request.args.get('start_lat')
    start_lon = request.args.get('start_lon')
    end_lat = request.args.get('end_lat')
    end_lon = request.args.get('end_lon')

    if not all([start_lat, start_lon, end_lat, end_lon]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
        end_lat = float(end_lat)
        end_lon = float(end_lon)
    except ValueError:
        return jsonify({"error": "Invalid latitude or longitude format"}), 400

    distance_km = round(calculate_distance(start_lat, start_lon, end_lat, end_lon))

    # Calculate number of intermediate points
    num_points = max(1, distance_km // 50)  # Ensure at least 1 point
    points = generate_intermediate_points(start_lat, start_lon, end_lat, end_lon, num_points)

    # Fetch terrain data for each intermediate point
    terrain_info = [fetch_terrain(lat, lon) for lat, lon in points]

    # Fetch terrain data for start and end points
    start_terrain = fetch_terrain(start_lat, start_lon)
    end_terrain = fetch_terrain(end_lat, end_lon)

    # Count occurrences of each terrain category in intermediate terrain info
    terrain_counts = Counter()
    for terrain in terrain_info:
        for category in terrain.split(', '):
            terrain_counts[category] += 1

    # Convert terrain counts to a list of dictionaries
    terrain_counts_list = [{"terrain": terrain, "count": count} for terrain, count in terrain_counts.items()]

    route_info = {
        "distance_km": distance_km,
        "intermediate_terrain_info": [
            {"lat": lat, "lon": lon, "terrain": terrain}
            for (lat, lon), terrain in zip(points, terrain_info)
        ] + [  # Add terrain counts to the end of the intermediate_terrain_info array
            {"terrain_counts": terrain_counts_list}
        ],
        "route": [
            {"lat": start_lat, "lon": start_lon, "terrain": start_terrain},
            {"lat": end_lat, "lon": end_lon, "terrain": end_terrain}
        ]
    }

    return jsonify({'status': 200, 'data': route_info})

def calculate_distance(start_lat, start_lon, end_lat, end_lon):
    start_point = (start_lat, start_lon)
    end_point = (end_lat, end_lon)
    return geodesic(start_point, end_point).km

def generate_intermediate_points(start_lat, start_lon, end_lat, end_lon, num_points):
    """Generate evenly spaced intermediate points between start and end points."""
    lats = np.linspace(start_lat, end_lat, num_points + 2)  # Including start and end
    lons = np.linspace(start_lon, end_lon, num_points + 2)  # Including start and end
    return list(zip(lats[1:-1], lons[1:-1]))  # Exclude start and end points

def fetch_terrain(lat, lon):
    """Fetch land use data from OpenStreetMap."""
    try:
        radius = 500  # Radius in meters for precision
        url = f"https://overpass-api.de/api/interpreter?data=[out:json][timeout:25];(node(around:{radius},{lat},{lon});way(around:{radius},{lat},{lon});relation(around:{radius},{lat},{lon}););out body;>;out skel qt;"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        land_use_types = set()
        for element in data.get('elements', []):
            if 'tags' in element:
                tags = element['tags']
                land_use = tags.get('landuse') or tags.get('natural')
                if land_use:
                    land_use_types.add(land_use)

        # Map land use types to categories
        categorized_terrain = categorize_terrain(land_use_types)

        if categorized_terrain:
            return ', '.join(categorized_terrain)
        return 'Unknown'
    except requests.RequestException as e:
        print(f"HTTP Request error: {e}")
        return 'Error: HTTP Request failed'
    except ValueError as e:
        print(f"JSON Parsing error: {e}")
        return 'Error: JSON Parsing failed'
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 'Error: Unexpected error'

def categorize_terrain(land_use_types):
    """Categorize terrain based on land use types."""
    terrain_categories = {
        'forest': {'forest', 'wood', 'scrub'},
        'water': {'water'},
        'flatlands': {'meadow', 'grass'},
        'urban': {'retail', 'commercial', 'industrial', 'brownfield'},
        'transport': {'railway'},
        'recreational': {'recreation_ground'},
        'agricultural': {'farmyard', 'farmland', 'orchard'},
        'military': {'military'},
        'cemetery': {'cemetery'},
        'unknown': {'Unknown'}
    }

    categorized_terrain = set()
    for category, types in terrain_categories.items():
        if land_use_types & types:
            categorized_terrain.add(category)
    
    return categorized_terrain

# ---- Run forever ---- $
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()
