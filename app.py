from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from optimizer import optimize_expression, parse_expression, optimize_multiple_lines  # Add this import

app = Flask(__name__)

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
    
    return jsonify({
        "asts": result["asts"],
        "steps": result["steps"],
        "variables": result["variables"]
    })

if __name__ == '__main__':
    app.run(debug=True)


