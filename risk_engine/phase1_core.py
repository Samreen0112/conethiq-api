import random
from datetime import datetime, timezone
from typing import Dict, Any

def calculate_eal_phase1(inputs: Dict[str, Any]) -> Dict[str, Any]:
    BASE_MULTIPLIER = 5
    random.seed(inputs.get("seed", 42))

    # Input extraction with defaults and bounds
    sla = min(max(inputs.get("SLA", 80), 0), 100)
    rto = max(inputs.get("RTO", 12), 0.1)
    fallback = str(inputs.get("fallback", "medium")).lower()
    direct_loss = max(inputs.get("direct_loss", 50000), 0)

    # TEF (threat event frequency) modifiers
    sla_factor = max(0.1, (100 - sla) / 100)
    rto_factor = min(2.0, rto / 12)
    fallback_weights = {"low": 1.5, "medium": 1.0, "high": 0.6}
    fallback_factor = fallback_weights.get(fallback, 1.0)

    # Final TEF calculation
    tef = sla_factor * rto_factor * fallback_factor * BASE_MULTIPLIER
    lef = tef  # In prototype, LEF is equal to TEF

    # Indirect loss modeled with log-normal distribution
    mu, sigma = -1, 0.6
    indirect_multiplier = min(random.lognormvariate(mu, sigma), 2.0)
    indirect_loss = direct_loss * indirect_multiplier
    lm = direct_loss + indirect_loss

    # EAL = LEF × LM
    eal = lef * lm

    return {
        "EAL (USD/year)": round(eal, 2),
        "LEF": round(lef, 2),
        "LM": round(lm, 2),
        "Direct Loss": direct_loss,
        "Indirect Loss (est.)": round(indirect_loss, 2),
        "SLA Factor": round(sla_factor, 2),
        "RTO Factor": round(rto_factor, 2),
        "Fallback Factor": round(fallback_factor, 2),
        "Indirect Multiplier": round(indirect_multiplier, 2),
        "Timestamp": datetime.now(timezone.utc).isoformat(),
        "Model Version": "proto-1.0",
        "Assumptions": (
            "EAL = LEF × LM\n"
            "TEF based on SLA, RTO, and fallback maturity\n"
            "Indirect loss modeled via log-normal distribution (μ=-1, σ=0.6)"
        )
    }

