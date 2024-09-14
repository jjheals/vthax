from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS
import pandas as pd
import numpy as np
from terrain import calculate_distance, generate_intermediate_points, fetch_terrain, count_terrain_categories

# ---- Init flask ---- #
app = Flask(__name__)
compress = Compress()
compress.init_app(app)

# Init CORS with the URL of the React app
CORS(app, origins=['http://localhost:3000'])

# ---- Init backend ---- #
# Load the data, graph, etc.
vehicles_df: pd.DataFrame = pd.read_csv('../../data/static/vehicle-definitions.csv')
terrain_df: pd.DataFrame = pd.read_csv('../../data/static/terrain-definitions.csv')
# Assuming you have a function df_to_graph in utils.py
from utils import df_to_graph
terrain_vehicle_matrix: np.matrix = df_to_graph(pd.read_csv('../../data/static/terrain-vehicle-matrix.csv'))

# ---- PROCESSING ---- #
def process_form_data(data):
    print("Form Data Received:", data)
    get_elevation(data['start-lat'], data['start-long'], data['end-lat'], data['end-lon'])
    return {'status': 'success', 'message': 'Form submitted successfully'}

# ---- ENDPOINTS ---- #
@app.route('/submit-form', methods=['POST'])
def submit_form():
    form_data = request.form
    result = process_form_data(dict(form_data))
    return jsonify(result)

@app.route('/get-input-params', methods=['GET'])
def get_input_params():
    data: dict = {
        'vehicles': [
            {
                'vehicle-id': r['vehicle_id'],
                'vehicle-name': r['vehicle_name'],
                'vehicle-description': r['description']
            } for idx, r in vehicles_df.iterrows()
        ],
        'strategies': [
            {
                'strategy-id': 'aggressive',
                'strategy-name': 'Aggressive'
            },
            {
                'strategy-id': 'stealth',
                'strategy-name': 'Stealth'
            }
        ],
        'objectives': [
            {
                'objective-id': 'def',
                'objective-name': 'Defensive (Hold position)'
            },
            {
                'objective-id': 'hvt',
                'objective-name': 'Capture/Extract HVT'
            },
            {
                'objective-id': 'inf',
                'objective-name': 'Infiltrate Target'
            }
        ]
    }

    return jsonify({'data': data})

def get_elevation(start_lat, start_lon, end_lat, end_lon):
    if not all([start_lat, start_lon, end_lat, end_lon]):
        return []

    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
        end_lat = float(end_lat)
        end_lon = float(end_lon)
    except ValueError:
        return []

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
    terrain_counts = count_terrain_categories(terrain_info)

    route_info = {
        "distance_km": distance_km,
        "intermediate_terrain_info": [
            {"lat": lat, "lon": lon, "terrain": terrain}
            for (lat, lon), terrain in zip(points, terrain_info)
        ] + [  # Add terrain counts to the end of the intermediate_terrain_info array
            {"terrain_counts": terrain_counts}
        ],
        "route": [
            {"lat": start_lat, "lon": start_lon, "terrain": start_terrain},
            {"lat": end_lat, "lon": end_lon, "terrain": end_terrain}
        ]
    }
    print(route_info)
    return {'status': 200, 'data': route_info}

# ---- Run forever ---- $
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()
