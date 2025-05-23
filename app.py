from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
import os
from optimizer import optimize_expression, parse_expression, optimize_multiple_lines

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    expr = data.get('expression')
    result = optimize_multiple_lines(expr)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


