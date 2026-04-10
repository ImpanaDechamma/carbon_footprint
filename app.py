from flask import Flask, jsonify, request
from predict import predict_future, predict_from_input

app = Flask(__name__)

@app.route('/')
def home():
    return "Carbon Footprint API is running!"

@app.route('/predict', methods=['GET'])
def predict():
    try:
        result = predict_future()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict_input', methods=['POST'])
def predict_input():
    try:
        data = request.get_json()
        print("Received data:", data)
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        result = predict_from_input(data)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)