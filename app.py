from flask import Flask, request, jsonify
from optimizer import optimize_expression

app = Flask(__name__)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    expr = data.get('expression')
    ast, steps = optimize_expression(expr)
    return jsonify({
        "optimized": steps[-1] if steps else expr,
        "steps": steps,
        "ast": ast.to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True)


