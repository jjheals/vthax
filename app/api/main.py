from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS
import pandas as pd
import numpy as np
from terrain import get_elevation

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
    def get_vehicles():
        vehicle_map = {
            'ft': 'Foot',
            'lv': 'Car',
            'hc': 'Helicopter',
            'bt': 'Boat'
        }

        selected_vehicles = ['Foot']

        for key, vehicle in vehicle_map.items():
            if key != 'ft' and data.get(key) == 'on':
                selected_vehicles.append(vehicle)

        return selected_vehicles
    
    vehicles = get_vehicles()
    print("Form Data Received:", data, '\n', vehicles)
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


# ---- Run forever ---- $
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()
