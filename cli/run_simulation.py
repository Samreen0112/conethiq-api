import json
from risk_engine.phase1_core import calculate_eal_phase1
from risk_engine.phase2_modifier import modifier_engine
from risk_engine.phase3_learning import adjust_lef_with_learning
from risk_engine.governance_layer import generate_audit_metadata
from risk_engine.confidence_index import calculate_confidence

print("🔧 Simulation started...")

# Load input data
try:
    with open("data/input.json") as f:
        input_data = json.load(f)
    print("📥 Loaded input.json successfully.")
except Exception as e:
    print("❌ ERROR: Failed to load input.json")
    print(e)
    exit(1)

# Phase 2: Apply modifier logic
try:
    modifiers = modifier_engine(input_data)
    print("🔍 Applied modifier_engine successfully.")
except Exception as e:
    print("❌ ERROR in modifier_engine:")
    print(e)
    exit(1)

input_data.update(modifiers)

# Phase 2.5: Compute LEF explicitly from modifier output
try:
    BASE_MULTIPLIER = 5
    input_data["LEF"] = (
        input_data["SLA Factor"]
        * input_data["RTO Factor"]
        * input_data["Fallback Factor"]
        * BASE_MULTIPLIER
    )
    print("🧮 LEF calculated from modifier output.")
except Exception as e:
    print("❌ ERROR in LEF computation:")
    print(e)
    exit(1)

# Phase 3: Adjust LEF with incident learning
try:
    learning = adjust_lef_with_learning(
        tef=input_data["LEF"],
        fallback=input_data["fallback"],
        num_incidents_last_year=input_data.get("num_incidents_last_year", 0)
    )
    input_data.update(learning)
    input_data["LEF"] = input_data["Adjusted LEF"]
    print("📚 Applied adaptive learning logic (Phase 3).")
except Exception as e:
    print("❌ ERROR in adaptive learning phase:")
    print(e)
    exit(1)

# Phase 1: Run core risk model using updated LEF
try:
    result = calculate_eal_phase1(input_data)
    print("📊 EAL calculation complete.")
except Exception as e:
    print("❌ ERROR in calculate_eal_phase1:")
    print(e)
    exit(1)

# Phase 4: Add governance metadata
try:
    audit = generate_audit_metadata(input_data)
    result["Governance"] = audit
    print("🔒 Governance metadata attached.")
except Exception as e:
    print("❌ ERROR in governance layer:")
    print(e)

# Phase 5: Confidence Index
try:
    confidence = calculate_confidence(result)
    result["Confidence Index"] = confidence
    print("📈 Confidence score calculated.")
except Exception as e:
    print("❌ ERROR in confidence index phase:")
    print(e)

# Add rationale to result
result["Modifier Rationale"] = modifiers.get("Rationale", [])
result["Learning Rationale"] = learning.get("Learning Rationale", [])

# Display final result
print("\n✅ Risk Simulation Result:")
for k, v in result.items():
    if isinstance(v, list):
        print(f"{k}:")
        for item in v:
            print(f"  - {item}")
    elif isinstance(v, dict):
        print(f"{k}:")
        for subk, subv in v.items():
            print(f"  - {subk}: {subv}")
    else:
        print(f"{k}: {v}")
