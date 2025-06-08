from flask import Flask, request, jsonify
from flask_cors import CORS

from risk_engine.phase1_core import calculate_eal_phase1
from risk_engine.phase2_modifier import modifier_engine
from risk_engine.phase3_learning import adjust_lef_with_learning
from risk_engine.governance_layer import generate_audit_metadata
from risk_engine.confidence_index import calculate_confidence

app = Flask(__name__)
CORS(app)  # 🔓 Allow frontend to call this API

@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        inputs = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Invalid JSON input", "details": str(e)}), 400

    modifiers = modifier_engine(inputs)
    inputs.update(modifiers)

    BASE_MULTIPLIER = 5
    inputs["LEF"] = (
        inputs["SLA Factor"]
        * inputs["RTO Factor"]
        * inputs["Fallback Factor"]
        * BASE_MULTIPLIER
    )

    learning = adjust_lef_with_learning(
        tef=inputs["LEF"],
        fallback=inputs["fallback"],
        num_incidents_last_year=inputs.get("num_incidents_last_year", 0)
    )
    inputs.update(learning)
    inputs["LEF"] = inputs["Adjusted LEF"]

    result = calculate_eal_phase1(inputs)
    result["Governance"] = generate_audit_metadata(inputs)
    result["Confidence Index"] = calculate_confidence(result)
    result["Modifier Rationale"] = modifiers.get("Rationale", [])
    result["Learning Rationale"] = learning.get("Learning Rationale", [])

    return jsonify(result)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "ConEthiq Risk Engine API is live."})

if __name__ == "__main__":
    app.run()
