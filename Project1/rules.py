"""
rules.py
--------
Individual rule functions for the AI Racing Strategy Agent.

Each function receives a RaceState and returns a list of human-readable
reason strings that triggered the rule, or an empty list if the rule
did NOT fire.

Design: every rule is self-contained and testable in isolation.
The strategy_engine.py module calls these rules in priority order and
assembles the final decision.
"""

from typing import List
from race_state import RaceState


# ===========================================================
# PIT RULES
# ===========================================================

def rule_tyre_critical(state: RaceState) -> List[str]:
    """
    PRIORITY 1 – Tyre condition is dangerously low.
    A tyre below 20% risks a puncture or sudden grip loss.
    → PIT immediately regardless of other conditions.
    """
    reasons: List[str] = []
    if state.tyre_condition < 20:
        reasons.append(
            f"Tyre condition is critically low ({state.tyre_condition:.1f}%) — risk of failure"
        )
    return reasons


def rule_tyre_low_many_laps(state: RaceState) -> List[str]:
    """
    PRIORITY 2 – Tyres are degraded and many laps remain.
    If tyres drop below 40% with more than 15 laps left, they will
    not survive to the end without a significant performance loss.
    → PIT to refresh the tyre strategy.
    """
    reasons: List[str] = []
    if state.tyre_condition < 40 and state.remaining_laps > 15:
        reasons.append(
            f"Tyre condition is low ({state.tyre_condition:.1f}%) with {state.remaining_laps} laps remaining"
        )
    return reasons


def rule_weather_pit(state: RaceState) -> List[str]:
    """
    PRIORITY 3 – Weather has changed to rain.
    Running slick (dry) tyres on a wet track is extremely dangerous.
    When rain is detected the car should switch to wet-weather tyres.
    Note: we assume current tyres are wrong for the weather when it
    is raining (a simplification suitable for this rule-based version).
    → PIT for tyre switch.
    """
    reasons: List[str] = []
    if state.is_raining and state.tyre_condition < 80:
        reasons.append(
            f"Weather changed to '{state.weather}' — tyre switch required"
        )
    return reasons


def rule_safe_gap_to_pit(state: RaceState) -> List[str]:
    """
    Supporting rule: gap behind is large enough for a pit stop
    without losing a position.  Used alongside pit decisions.
    A gap > 20 seconds is typically safe for a ~22-second stop.
    """
    reasons: List[str] = []
    if state.gap_behind > 20:
        reasons.append(
            f"Gap behind ({state.gap_behind:.1f} sec) is large enough for a safe pit stop"
        )
    return reasons


# ===========================================================
# FUEL / CONSERVE RULES
# ===========================================================

def rule_fuel_critical(state: RaceState) -> List[str]:
    """
    PRIORITY 4 – Fuel is critically low relative to remaining laps.
    Fuel consumption is roughly proportional to laps.
    Rule of thumb: fuel_per_lap ≈ 3% (simplified).
    If current fuel cannot cover remaining laps, conserve immediately.
    → CONSERVE
    """
    reasons: List[str] = []
    estimated_fuel_needed = state.remaining_laps * 3.0
    if state.fuel < estimated_fuel_needed and state.fuel < 30:
        reasons.append(
            f"Fuel at {state.fuel:.1f}% — estimated {estimated_fuel_needed:.1f}% needed for "
            f"{state.remaining_laps} remaining laps"
        )
    return reasons


def rule_fuel_low_comfortable_position(state: RaceState) -> List[str]:
    """
    PRIORITY 5 – Fuel is low but the car holds a strong position.
    When fuel drops below 25% and the car is inside the top 5,
    it is smarter to conserve fuel than to risk running out.
    → CONSERVE
    """
    reasons: List[str] = []
    if state.fuel < 25 and state.position <= 5 and state.gap_behind > 3:
        reasons.append(
            f"Fuel at {state.fuel:.1f}% — conserving fuel to protect P{state.position}"
        )
    return reasons


# ===========================================================
# ATTACK RULES
# ===========================================================

def rule_attack_opportunity(state: RaceState) -> List[str]:
    """
    PRIORITY 6 – Strong overtaking opportunity.
    Conditions required:
      • Gap to car ahead ≤ 1.0 second (DRS zone range)
      • Tyre condition ≥ 50% (enough grip to push)
      • Fuel ≥ 30% (enough to manage pace)
      • Not in P1 (no one ahead to attack)
    → ATTACK
    """
    reasons: List[str] = []
    if (
        state.gap_ahead <= 1.0
        and state.tyre_condition >= 50
        and state.fuel >= 30
        and state.position > 1
    ):
        reasons.append(
            f"Gap to car ahead is {state.gap_ahead:.2f} sec — DRS overtaking range"
        )
        reasons.append(
            f"Tyres at {state.tyre_condition:.1f}% — sufficient grip to push"
        )
        reasons.append(
            f"Fuel at {state.fuel:.1f}% — enough to sustain attack pace"
        )
    return reasons


def rule_attack_final_laps(state: RaceState) -> List[str]:
    """
    PRIORITY 6b – Final-lap attack opportunity.
    In the last 5 laps, any gap ≤ 2 seconds is an attack opportunity
    because there are limited laps left to recover position.
    """
    reasons: List[str] = []
    if (
        state.remaining_laps <= 5
        and state.gap_ahead <= 2.0
        and state.tyre_condition >= 40
        and state.position > 1
    ):
        reasons.append(
            f"Only {state.remaining_laps} laps remain — time to push for position"
        )
        reasons.append(
            f"Gap to car ahead is {state.gap_ahead:.2f} sec — within striking range"
        )
    return reasons


# ===========================================================
# DEFEND RULES
# ===========================================================

def rule_defend_under_pressure(state: RaceState) -> List[str]:
    """
    PRIORITY 7 – Car is under threat from behind.
    Conditions:
      • Gap from car behind ≤ 1.0 second (threat in DRS range)
      • Tyre condition < 50% (tyres not ideal for racing hard)
    Defending the position is more important than attacking.
    → DEFEND
    """
    reasons: List[str] = []
    if state.gap_behind <= 1.0 and state.tyre_condition < 50:
        reasons.append(
            f"Car behind is only {state.gap_behind:.2f} sec away — in DRS range"
        )
        reasons.append(
            f"Tyre condition is {state.tyre_condition:.1f}% — not ideal for sustained attack"
        )
    return reasons


def rule_defend_protect_points(state: RaceState) -> List[str]:
    """
    PRIORITY 7b – Defending a points position.
    Formula 1 points positions are P1–P10.
    If inside top 10, low on fuel, and a rival is closing:
    → DEFEND
    """
    reasons: List[str] = []
    if (
        state.position <= 10
        and state.gap_behind <= 1.5
        and state.fuel < 20
    ):
        reasons.append(
            f"P{state.position} is a points position worth protecting"
        )
        reasons.append(
            f"Rival is {state.gap_behind:.2f} sec behind with low fuel ({state.fuel:.1f}%) — must defend"
        )
    return reasons


# ===========================================================
# STAY OUT RULES
# ===========================================================

def rule_stay_out(state: RaceState) -> List[str]:
    """
    PRIORITY 8 – Default: stay out on track.
    Conditions for staying out:
      • Tyre condition ≥ 40%  (healthy enough to continue)
      • Fuel ≥ 30%
      • Weather is dry (no rain threat)
      • No immediate threat from behind (gap > 1.0 sec)
    → STAY OUT
    """
    reasons: List[str] = []
    if (
        state.tyre_condition >= 40
        and state.fuel >= 30
        and not state.is_raining
        and state.gap_behind > 1.0
    ):
        reasons.append(
            f"Tyre condition is adequate ({state.tyre_condition:.1f}%) — no need to pit"
        )
        reasons.append(
            f"Fuel level is sufficient ({state.fuel:.1f}%)"
        )
        reasons.append("Weather is stable — no strategy change required")
    return reasons
