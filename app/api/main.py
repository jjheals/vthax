from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS
import pandas as pd
import numpy as np
from terrain import get_elevation, create_triangular_paths
from utils import df_to_graph

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

    print("Form Data Received:", data)

    get_elevation(data['start-lat'], data['start-long'], data['end-lat'], data['end-lon'])

    paths = create_triangular_paths(
        (float(data['start-lat']), float(data['start-long'])),
        (float(data['end-lat']), float(data['end-lon'])),
        5, 
        4,
        0.4
    )

    print('created paths')

    return {'status': 'success', 'message': 'Form submitted successfully', 'paths': paths}


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
