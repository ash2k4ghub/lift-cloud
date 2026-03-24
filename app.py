from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

lift_data = []

@app.route("/")
def home():
    return "Lift Cloud Server Running"

@app.route("/update", methods=["POST"])
def update():
    global lift_data
    lift_data = request.json or []
    return {"status": "updated"}

@app.route("/status")
def status():
    return jsonify(lift_data)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))