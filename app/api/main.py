from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from flask_cors import CORS 

# ---- Init flask ---- #
app = Flask(__name__)
compress = Compress()
compress.init_app(app)

# Init CORS with the URL of the React app
CORS(app, origins=['http://localhost:3000'])  


# ---- ENDPOINTS ---- #
@app.route('/generate-plan', methods=['GET'])
def generate_plan():

    # TODO: process input params and generate a plan to return 
    # DO SOMETHING 
    # ...

    return jsonify({'status': 200, 'data': {}})


# ---- Run forever ---- $
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()