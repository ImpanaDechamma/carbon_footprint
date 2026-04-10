from flask import Flask, jsonify, request
from predict import predict_future, predict_from_input

app = Flask(__name__)

@app.route('/')
def home():
    return "Carbon Footprint API is running!"

@app.route('/predict', methods=['GET'])
def predict():
    try:
        server_id = request.args.get("server_id", "S1")
        region    = request.args.get("region", "USA")
        steps     = int(request.args.get("steps", 3))
        result    = predict_future(server_id=server_id, region=region, steps=steps)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict_input', methods=['POST'])
def predict_input():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        result = predict_from_input(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
