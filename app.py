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

    try:
        boarding = int(request.args.get("boarding"))
        destination = int(request.args.get("destination"))

        # 🚨 safety check
        if not lift_data:
            return jsonify({
                "best_lift": "None",
                "eta": -1,
                "mode": "NO DATA"
            })

        best_lift = None
        best_eta = float("inf")

        for lift in lift_data:

            # -------- SAFE READ --------
            current_floor = lift.get("floor", 0)
            state = lift.get("state", "IDLE")
            remaining_pulses = lift.get("remaining_pulses", 0)
            total_pulses = lift.get("total_pulses", 0)
            target_floor = lift.get("target_floor", current_floor)

            # -------- DIRECT ETA (EXACT LOGIC) --------
            distance = abs(current_floor - boarding)
            pulses = distance * PULSES_PER_FLOOR
            travel_time = pulses * PULSE_TIME

            if current_floor == boarding and state == "IDLE":
                direct_eta = 0

            elif state == "IDLE":
                direct_eta = travel_time

            elif state == "MOVING":
                remaining_time = remaining_pulses * PULSE_TIME
                direct_eta = remaining_time + STOP_TIME + travel_time

            elif state == "STOPPING":
                remaining_stop = STOP_TIME
                direct_eta = remaining_stop + travel_time

            else:
                direct_eta = 9999

            # -------- FUTURE ETA --------
            if state == "MOVING":

                finish_time = remaining_pulses * PULSE_TIME + STOP_TIME

                future_distance = abs(target_floor - boarding)
                future_travel = future_distance * PULSES_PER_FLOOR * PULSE_TIME

                future_eta = finish_time + future_travel

            elif state == "STOPPING":

                remaining_stop = STOP_TIME

                future_distance = abs(current_floor - boarding)
                future_travel = future_distance * PULSES_PER_FLOOR * PULSE_TIME

                future_eta = remaining_stop + future_travel

            else:
                future_eta = direct_eta

            # -------- FINAL --------
            chosen_eta = min(direct_eta, future_eta)

            if chosen_eta < best_eta:
                best_eta = chosen_eta
                best_lift = lift

        return jsonify({
            "best_lift": best_lift["name"] if best_lift else "None",
            "eta": int(best_eta) if best_lift else -1,
            "mode": "SMART-FUTURE-AWARE"
        })

    except Exception as e:
        print("RECOMMEND ERROR:", e)
        return jsonify({
            "best_lift": "Error",
            "eta": -1,
            "mode": "ERROR"
        })
if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
