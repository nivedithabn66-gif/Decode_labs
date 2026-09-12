"""
strategy_engine.py
------------------
The core decision engine of the AI Racing Strategy Agent.

Architecture
------------
This module implements a PRIORITY-BASED rule evaluation system:

  Priority 1  → Critical tyre failure risk        → PIT
  Priority 2  → Low tyres + many laps remaining   → PIT
  Priority 3  → Weather changed, wrong tyres      → PIT
  Priority 4  → Critical fuel level               → CONSERVE
  Priority 5  → Low fuel in comfortable position  → CONSERVE
  Priority 6  → Attack opportunity (DRS range)    → ATTACK
  Priority 6b → Final-lap attack                  → ATTACK
  Priority 7  → Under threat from behind          → DEFEND
  Priority 7b → Defending a points position       → DEFEND
  Priority 8  → Default healthy conditions        → STAY OUT
  Fallback    → When no rule fires cleanly        → CONSERVE (safe default)

Each rule returns a list of reason strings. The engine collects ALL
triggered reasons for the highest-priority fired rule and assembles the
final StrategyResult.

Explainability
--------------
No decision is silent. Every StrategyResult carries human-readable
reasons and a recommended action sentence so the user always knows WHY
the agent made its choice.
"""

from dataclasses import dataclass, field
from typing import List

from race_state import RaceState
import rules


# ===========================================================
# Result container
# ===========================================================

@dataclass
class StrategyResult:
    """
    Holds the complete output of a strategy evaluation.

    Attributes
    ----------
    decision       : The strategy keyword (PIT, STAY OUT, ATTACK, DEFEND, CONSERVE).
    reasons        : Human-readable list of rules that triggered this decision.
    recommendation : A plain-English action for the driver/team to take.
    """
    decision: str
    reasons: List[str] = field(default_factory=list)
    recommendation: str = ""


# ===========================================================
# Recommendation sentences
# ===========================================================

RECOMMENDATIONS = {
    "PIT": (
        "Box this lap. Switch to a suitable tyre compound and resume racing "
        "at full pace as quickly as possible."
    ),
    "STAY OUT": (
        "Continue on current strategy. Monitor tyre and fuel levels closely "
        "and reassess each lap."
    ),
    "ATTACK": (
        "Push hard and attempt the overtake. Use DRS if available and commit "
        "to the move on the braking zone."
    ),
    "DEFEND": (
        "Hold your line on corner entry. Protect the inside and brake late "
        "to prevent the car behind from passing."
    ),
    "CONSERVE": (
        "Lift and coast on the straights. Avoid wheelspin and protect the "
        "tyres and fuel for the critical laps ahead."
    ),
}


# ===========================================================
# Main evaluation function
# ===========================================================

def evaluate(state: RaceState) -> StrategyResult:
    """
    Evaluates the current race state through the priority-ordered rule
    chain and returns a fully explained StrategyResult.

    Parameters
    ----------
    state : The current RaceState snapshot.

    Returns
    -------
    StrategyResult containing the decision, all triggered reasons,
    and a recommended action sentence.
    """

    # ----------------------------------------------------------
    # PRIORITY 1 — Critical tyre condition → immediate PIT
    # ----------------------------------------------------------
    reasons_p1 = rules.rule_tyre_critical(state)
    if reasons_p1:
        gap_reasons = rules.rule_safe_gap_to_pit(state)
        return StrategyResult(
            decision="PIT",
            reasons=reasons_p1 + gap_reasons + [f"{state.remaining_laps} laps remaining"],
            recommendation=RECOMMENDATIONS["PIT"],
        )

    # ----------------------------------------------------------
    # PRIORITY 2 — Degraded tyres with many laps remaining → PIT
    # ----------------------------------------------------------
    reasons_p2 = rules.rule_tyre_low_many_laps(state)
    if reasons_p2:
        gap_reasons = rules.rule_safe_gap_to_pit(state)
        return StrategyResult(
            decision="PIT",
            reasons=reasons_p2 + gap_reasons,
            recommendation=RECOMMENDATIONS["PIT"],
        )

    # ----------------------------------------------------------
    # PRIORITY 3 — Weather-driven tyre strategy change → PIT
    # ----------------------------------------------------------
    reasons_p3 = rules.rule_weather_pit(state)
    if reasons_p3:
        gap_reasons = rules.rule_safe_gap_to_pit(state)
        return StrategyResult(
            decision="PIT",
            reasons=reasons_p3 + gap_reasons,
            recommendation=RECOMMENDATIONS["PIT"],
        )

    # ----------------------------------------------------------
    # PRIORITY 4 — Critical fuel level → CONSERVE
    # ----------------------------------------------------------
    reasons_p4 = rules.rule_fuel_critical(state)
    if reasons_p4:
        return StrategyResult(
            decision="CONSERVE",
            reasons=reasons_p4,
            recommendation=RECOMMENDATIONS["CONSERVE"],
        )

    # ----------------------------------------------------------
    # PRIORITY 5 — Low fuel but comfortable position → CONSERVE
    # ----------------------------------------------------------
    reasons_p5 = rules.rule_fuel_low_comfortable_position(state)
    if reasons_p5:
        return StrategyResult(
            decision="CONSERVE",
            reasons=reasons_p5,
            recommendation=RECOMMENDATIONS["CONSERVE"],
        )

    # ----------------------------------------------------------
    # PRIORITY 6 — DRS overtaking opportunity → ATTACK
    # ----------------------------------------------------------
    reasons_p6 = rules.rule_attack_opportunity(state)
    if reasons_p6:
        return StrategyResult(
            decision="ATTACK",
            reasons=reasons_p6,
            recommendation=RECOMMENDATIONS["ATTACK"],
        )

    # ----------------------------------------------------------
    # PRIORITY 6b — Final-lap push → ATTACK
    # ----------------------------------------------------------
    reasons_p6b = rules.rule_attack_final_laps(state)
    if reasons_p6b:
        return StrategyResult(
            decision="ATTACK",
            reasons=reasons_p6b,
            recommendation=RECOMMENDATIONS["ATTACK"],
        )

    # ----------------------------------------------------------
    # PRIORITY 7 — Under pressure from behind → DEFEND
    # ----------------------------------------------------------
    reasons_p7 = rules.rule_defend_under_pressure(state)
    if reasons_p7:
        return StrategyResult(
            decision="DEFEND",
            reasons=reasons_p7,
            recommendation=RECOMMENDATIONS["DEFEND"],
        )

    # ----------------------------------------------------------
    # PRIORITY 7b — Protecting a points finish → DEFEND
    # ----------------------------------------------------------
    reasons_p7b = rules.rule_defend_protect_points(state)
    if reasons_p7b:
        return StrategyResult(
            decision="DEFEND",
            reasons=reasons_p7b,
            recommendation=RECOMMENDATIONS["DEFEND"],
        )

    # ----------------------------------------------------------
    # PRIORITY 8 — All conditions good → STAY OUT
    # ----------------------------------------------------------
    reasons_p8 = rules.rule_stay_out(state)
    if reasons_p8:
        return StrategyResult(
            decision="STAY OUT",
            reasons=reasons_p8,
            recommendation=RECOMMENDATIONS["STAY OUT"],
        )

    # ----------------------------------------------------------
    # FALLBACK — Ambiguous conditions → CONSERVE (safest choice)
    # ----------------------------------------------------------
    return StrategyResult(
        decision="CONSERVE",
        reasons=[
            "Conditions are ambiguous — erring on the side of caution",
            f"Tyre: {state.tyre_condition:.1f}%  |  Fuel: {state.fuel:.1f}%  |  Weather: {state.weather}",
        ],
        recommendation=RECOMMENDATIONS["CONSERVE"],
    )
