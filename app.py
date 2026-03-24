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

    best_lift = None
    best_eta = float("inf")

    for lift in lift_data:

        current_floor = lift["floor"]
        state = lift["state"]
        remaining_pulses = lift["remaining_pulses"]
        target_floor = lift["target_floor"]

        # -------- DIRECT ETA --------
        distance = abs(current_floor - boarding)
        pulses = distance * PULSES_PER_FLOOR
        direct_eta = pulses * PULSE_TIME

        # -------- FUTURE ETA --------
        future_eta = float("inf")

        if state == "MOVING":

            finish_time = remaining_pulses * PULSE_TIME + STOP_TIME

            future_distance = abs(target_floor - boarding)
            future_travel = future_distance * PULSES_PER_FLOOR * PULSE_TIME

            future_eta = finish_time + future_travel

        elif state == "STOPPING":

            # we don't have stop_start in cloud → approximate
            remaining_stop = STOP_TIME

            future_distance = abs(current_floor - boarding)
            future_travel = future_distance * PULSES_PER_FLOOR * PULSE_TIME

            future_eta = remaining_stop + future_travel

        else:
            future_eta = direct_eta

        # -------- FINAL SELECTION --------
        chosen_eta = min(direct_eta, future_eta)

        if chosen_eta < best_eta:
            best_eta = chosen_eta
            best_lift = lift

    return jsonify({
        "best_lift": best_lift["name"],
        "eta": int(best_eta),
        "mode": "SMART-FUTURE-AWARE"
    })
if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
