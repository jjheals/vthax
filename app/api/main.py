from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS
import pandas as pd
import numpy as np
from terrain import create_triangular_paths, fetch_terrain, calculate_distance
from flask_cors import CORS
import pandas as pd
import numpy as np
from terrain import create_triangular_paths, fetch_terrain, calculate_distance
from utils import df_to_graph
from gpt_utils import get_chatgpt_response, format_prompt
from path_model import get_top_5_combinations

from concurrent.futures import ThreadPoolExecutor
import json
from collections import Counter
from country import get_country_from_coords
import datetime as dt 
from gpt_utils import get_chatgpt_response, format_prompt
from path_model import get_top_5_combinations

from concurrent.futures import ThreadPoolExecutor
import json
from collections import Counter
from country import get_country_from_coords
import datetime as dt 


# ---- Init flask ---- #
app = Flask(__name__)
compress = Compress()
compress.init_app(app)

# Init CORS with the URL of the React app
CORS(app, origins=['http://localhost:3000'])
CORS(app, origins=['http://localhost:3000'])

# ---- Init backend ---- #
# Load the data, graph, etc.
vehicles_df: pd.DataFrame = pd.read_csv('../../data/static/vehicle-definitions.csv')
terrain_df: pd.DataFrame = pd.read_csv('../../data/static/terrain-definitions.csv')
terrain_vehicle_matrix: np.matrix = df_to_graph(pd.read_csv('../../data/static/terrain-vehicle-matrix.csv'))
strategies_df:pd.DataFrame = pd.read_csv('../../data/static/strategy-definitions.csv')

with open('../../data/static/cost-matrix.json', 'r') as file:
    cost_matrix_json:dict = json.load(file)

# ---- PROCESSING ---- #

def process_form_data(data):

    # -- Generating paths -- #
    # Create paths with triangular deviations
    paths = create_triangular_paths(
        (float(data['start-lat']), float(data['start-lon'])),
        (float(data['end-lat']), float(data['end-lon'])),
        5,  # Number of paths
        4,  # Number of path breaks
        0.4  # Deviation factor
    )

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

    # Get the terrains from the terrain counts
    terrains:list[str] = []
    for d in terrain_count_with_paths.values():
        these_terrains:list[str] = d['terrain_counts'].keys()
        terrains.extend(these_terrains)
    
    terrains = list(set(terrains))
    
    # Get the vehicles based on the inputs 
    all_vehicle_ids:list[str] = vehicles_df['vehicle_id'].values
    vehicles:list[str] = []
    for vid in all_vehicle_ids: 
        if vid in data: 
            vehicles.append(vehicles_df.loc[vehicles_df['vehicle_id'] == vid]['vehicle_name'].values[0])

    # -- Generate an AI response -- #
    api_key:str = data.get('openai-api-key', '')
    model_name:str = data.get('openai-model', '')

    # If given an API key and model name, generate an AI response
    if api_key and model_name: 

        # Create a dict with the input params to construct the prompt for the model
        model_prompt_inputs:dict = {
            'vehicles': vehicles,
            'start-location': (data['start-lat'], data['start-lon']),
            'start-country': get_country_from_coords(data['start-lat'], data['start-lon']),
            'target-location': (data['end-lat'], data['end-lon']),
            'straight-distance': calculate_distance(data['start-lat'], data['start-lon'], data['end-lat'], data['end-lon']),
            'terrains': terrains,
            'total-personnel': data['personnel'],
            'target-time-on-obj': data['target-time-on-obj'],
            'expected-resistance': data['resistance'],
            'strategy': data['strategy'], 
            'strategy-description': strategies_df.loc[strategies_df['strategy_name'] == data['strategy']]['strategy_description'].values[0],
            'primary-objective': data['objective'],
            'additional-context': data['context']
        }

        # Use the OpenAI API to get a response from chatgpt
        response:str = get_chatgpt_response(
            format_prompt(model_prompt_inputs),
            data['openai-api-key'],
            data['openai-model']
        )
    else: 
        response:str = "[Not given OpenAI API key or model name]"

    # Get the top five paths to return to the client
    top_five_paths = get_top_5_combinations(terrain_count_with_paths, cost_matrix_json, vehicles)

    # Return the result with paths and terrain counts
    return {
        'status': 'success',
        'message': 'Form submitted successfully',
        'paths': terrain_count_with_paths,
        'ai_response': response,
        'top-paths': top_five_paths
    }


# ---- ENDPOINTS ---- #
@app.route('/api/submit-form', methods=['POST'])
def submit_form():
    print(f'\n\033[0m[{dt.datetime.now().strftime("%H:%M:%S")}] \033[92mForm submission.\033[0m')

    # Get the form data from the request and process it
    result = process_form_data(dict(request.form))

    # Info print
    print(f'\033[0m[{dt.datetime.now().strftime("%H:%M:%S")}] \033[92mDone. Returning.\033[0m\n')

    return jsonify(result)


@app.route('/api/get-input-params', methods=['GET'])
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


# ---- Run forever ---- $
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()