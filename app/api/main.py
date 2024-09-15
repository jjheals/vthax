from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS

import pandas as pd
import numpy as np
import json
import datetime as dt 
import random 

from terrain import create_triangular_paths, fetch_terrain_for_paths, calculate_distance
from utils import df_to_graph, key_with_lowest_sum
from country import get_country_from_coords
from gpt_utils import get_chatgpt_response, format_prompt
from path_model import get_top_5_combinations
from weather import find_best_time_window


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
strategies_df:pd.DataFrame = pd.read_csv('../../data/static/strategy-definitions.csv')

with open('../../data/static/cost-matrix.json', 'r') as file:
    cost_matrix_json:dict = json.load(file)


# ---- PROCESSING ---- #

def process_form_data(data):

    # -- Generating paths -- #
    # Create paths with triangular deviations
    start_point:tuple[float, float] = (float(data['start-lat']), float(data['start-lon']))
    end_point:tuple[float, float] = (float(data['end-lat']), float(data['end-lon']))

    paths = create_triangular_paths(
        start_point,
        end_point,
        5,                              # Number of paths
        4,
        round(random.uniform(0,1), 1)   # Deviation factor
    )

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
    print("The top five paths are as follows: ", top_five_paths)

    # Get the API Key for the weather functionality
    with open('weather_api.json', 'r') as file:
        weather_api_key = json.load(file)['api_key']

    # Best time window to execute the mission weatherwise
    print("STARTING TO RUN WEATHER PROCESS")
    current_date = dt.datetime.now()
    end_date = dt.datetime.strptime(data['latest-date'], "%Y-%m-%d")
    best_time_window, best_vehicle, best_cost, best_weather_conditions = find_best_time_window(weather_api_key, data['end-lat'], data['end-lon'], current_date, min(end_date, current_date + dt.timedelta(days=10)), int(data['target-time-on-obj']), vehicles, data['strategy'], data['objective'])
    
    print(f"Best Time Window: {best_time_window}")
    print(f"Best Vehicle: {best_vehicle}")
    print(f"Weather Conditions: {best_weather_conditions}")

    best_weather_conditions = ', '.join(list(set(best_weather_conditions)))

    # Return the result with paths and terrain counts
    return {
        'status': 'success',
        'message': 'Form submitted successfully',
        'paths': terrain_count_with_paths,
        'ai_response': response,
        'optimal_set': {
            'weather': best_weather_conditions,
            'vehicle': best_vehicle,
            'time_frame': best_time_window,
            'path': key_with_lowest_sum(top_five_paths)
        }
        #'top_paths': top_five_paths
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