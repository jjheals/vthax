from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS
import pandas as pd
import numpy as np
from terrain import create_triangular_paths, fetch_terrain
from utils import df_to_graph
from concurrent.futures import ThreadPoolExecutor
import json
from collections import Counter


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
terrain_vehicle_matrix: np.matrix = df_to_graph(pd.read_csv('../../data/static/terrain-vehicle-matrix.csv'))


# ---- PROCESSING ---- #

def process_form_data(data):
    print ('BREAK THIS IS A BREAK')
    print("Form Data Received:", data)

    # Create paths with triangular deviations
    paths = create_triangular_paths(
        (float(data['start-lat']), float(data['start-long'])),
        (float(data['end-lat']), float(data['end-lon'])),
        5,  # Number of paths
        4,  # Number of path breaks
        0.4  # Deviation factor
    )

    print('Created paths')

    def fetch_terrain_for_paths(paths):
        """Fetch terrain information for each path and count occurrences of each terrain type."""
        
        def fetch_terrain_for_single_path(path):
            """Fetch terrain info for a single path and count terrain types."""
            terrain_counts = Counter()
            for lat, lon in path:
                try:
                    terrain_info = fetch_terrain(lat, lon)
                    terrain_types = terrain_info.split(', ')
                    for terrain_type in terrain_types:
                        if terrain_type != "Unknown":
                            terrain_counts[terrain_type] += 1
                except Exception as e:
                    print(f"Error fetching terrain for ({lat}, {lon}): {e}")

            # Fetch terrain for midpoints as well
            for i in range(len(path) - 1):
                lat1, lon1 = path[i]
                lat2, lon2 = path[i + 1]

                # Compute midpoint
                mid_lat = (lat1 + lat2) / 2
                mid_lon = (lon1 + lon2) / 2

                try:
                    terrain_info = fetch_terrain(mid_lat, mid_lon)
                    for terrain_type in terrain_info.split(', '):
                        if terrain_type != "Unknown":
                            terrain_counts[terrain_type] += 1
                except Exception as e:
                    print(f"Error fetching terrain for midpoint ({mid_lat}, {mid_lon}): {e}")

            return terrain_counts

        # Use ThreadPoolExecutor to process each path in parallel
        with ThreadPoolExecutor(max_workers=min(len(paths), 10)) as executor:
            # Map paths to the terrain counting function
            terrain_counts_list = list(executor.map(fetch_terrain_for_single_path, paths))

        # Convert to the required format
        result = {
            f'Path {i + 1}': {
                'path': paths[i],
                'terrain_counts': dict(terrain_counts_list[i])
            }
            for i in range(len(paths))
        }

        return result


    # Fetch terrain counts for each path
    terrain_count_with_paths = fetch_terrain_for_paths(paths)

    # Write terrain counts to a file
    with open('tmp.json', 'w+') as file:
        json.dump(terrain_count_with_paths, file, indent=4)

    print('Done processing')

    # Return the result with paths and terrain counts
    return {
        'status': 'success',
        'message': 'Form submitted successfully',
        'terrain_counts': terrain_count_with_paths  # Include terrain counts in the result
    }


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


@app.route('/get-paths', methods=['GET'])
def get_paths(): 
    args = request.args
    print('args')
    print(args)


    return jsonify({'paths': create_triangular_paths()})

# ---- Run forever ---- $
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()
