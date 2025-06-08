import json
import copy
from risk_engine.phase1_core import calculate_eal_phase1
from risk_engine.phase2_modifier import modifier_engine
from risk_engine.phase3_learning import adjust_lef_with_learning
from risk_engine.governance_layer import generate_audit_metadata
from risk_engine.confidence_index import calculate_confidence

print("🔁 Scenario Sensitivity Simulation Starting...\n")

# Load base scenario
try:
    with open("data/input.json") as f:
        base_input = json.load(f)
except Exception as e:
    print("❌ ERROR loading input.json:", e)
    exit(1)

# Parameter sweep: try different fallback values
fallback_values = ["low", "medium", "high"]
results = []

for fallback in fallback_values:
    scenario = copy.deepcopy(base_input)
    scenario["fallback"] = fallback

    # Phase 2: Modifiers
    modifiers = modifier_engine(scenario)
    scenario.update(modifiers)

    # LEF
    BASE_MULTIPLIER = 5
    scenario["LEF"] = (
        scenario["SLA Factor"]
        * scenario["RTO Factor"]
        * scenario["Fallback Factor"]
        * BASE_MULTIPLIER
    )

    # Phase 3: Learning
    learning = adjust_lef_with_learning(
        tef=scenario["LEF"],
        fallback=scenario["fallback"],
        num_incidents_last_year=scenario.get("num_incidents_last_year", 0)
    )
    scenario.update(learning)
    scenario["LEF"] = scenario["Adjusted LEF"]

    # Phase 1: Risk calculation
    result = calculate_eal_phase1(scenario)

    # Phase 4: Governance
    result["Governance"] = generate_audit_metadata(scenario)

    # Phase 5: Confidence
    result["Confidence Index"] = calculate_confidence(result)

    result["fallback"] = fallback
    result["Adjusted LEF"] = scenario["Adjusted LEF"]
    results.append(result)

# Print all results
print("📊 Scenario Results:\n")
for res in results:
    print(f"Fallback: {res['fallback']}")
    print(f"  EAL (USD/year): {res['EAL (USD/year)']}")
    print(f"  Adjusted LEF: {res['Adjusted LEF']}")
    print(f"  Confidence: {res['Confidence Index']['confidence_score']}")
    print(f"  Input Quality: {res['Governance']['input_quality_score']}")
    print("  ---")

print("\n✅ Scenario simulation complete.")
