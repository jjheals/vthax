from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS 
import pandas as pd 
import numpy as np 

from utils import df_to_graph


# ---- Init flask ---- #
app = Flask(__name__)
compress = Compress()
compress.init_app(app)

# Init CORS with the URL of the React app
CORS(app, origins=['http://localhost:3000'])  

# ---- Init backend ---- #
# Load the data, graph, etc. 
vehicles_df:pd.DataFrame = pd.read_csv('../../data/static/vehicle-definitions.csv')
terrain_df:pd.DataFrame = pd.read_csv('../../data/static/terrain-definitions.csv')
terrain_vehicle_matrix:np.matrix = df_to_graph(pd.read_csv('../../data/static/terrain-vehicle-matrix.csv'))

# ---- ENDPOINTS ---- #
@app.route('/generate-plan', methods=['GET'])
def generate_plan():
    """ Returns the plan for the given input parameters. """
    # TODO: process input params and generate a plan to return 
    # DO SOMETHING 
    # ...

    return jsonify({'status': 200, 'data': {}})


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



# ---- Run forever ---- $
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()