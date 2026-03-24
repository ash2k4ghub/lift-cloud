from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import render_template

app = Flask(__name__)
CORS(app)

lift_data = []

@app.route("/")
def home():
    return render_template("index - Copy.html")

@app.route("/update", methods=["POST"])
def update():
    global lift_data
    lift_data = request.json or []
    return {"status": "updated"}

@app.route("/status")
def status():
    return jsonify(lift_data)

@app.route("/recommend")
def recommend():

    boarding = int(request.args.get("boarding"))
    destination = int(request.args.get("destination"))

    user_direction = "UP" if destination > boarding else "DOWN"

    best = None
    best_eta = float("inf")

    for lift in lift_data:

        floor = lift["floor"]
        eta = lift["eta"]

        # direction logic
        if floor < boarding:
            direction = "UP"
        elif floor > boarding:
            direction = "DOWN"
        else:
            direction = user_direction

        if direction == user_direction and eta < best_eta:
            best_eta = eta
            best = lift

    if best:
        return jsonify({
            "best_lift": best["name"],
            "eta": best_eta,
            "mode": "STRICT"
        })

    return jsonify({
        "best_lift": "None",
        "eta": -1,
        "mode": "FALLBACK"
    })

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
