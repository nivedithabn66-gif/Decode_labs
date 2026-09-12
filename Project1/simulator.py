"""
simulator.py
------------
Race Simulation Mode for the AI Racing Strategy Agent.

The simulator generates deterministic race conditions lap by lap and
feeds them through the strategy engine to demonstrate how decisions
evolve across a full race distance.

Design philosophy
-----------------
- Simple and deterministic (no randomness, no physics engine)
- Each lap updates fuel, tyre wear, and simulated gaps
- Weather can change mid-race at predefined lap triggers
- Pit stops are tracked and applied when the agent recommends PIT

This module is intentionally simplified so the user can trace
every state change and understand the agent's behaviour.
"""

import time
from typing import Optional

from race_state import RaceState
from strategy_engine import evaluate, StrategyResult
from utils import print_divider, print_decision, BOLD, RESET, CYAN, GREEN, YELLOW


# ===========================================================
# Simulation constants (tunable)
# ===========================================================

# Approximate tyre wear per lap (%)
TYRE_WEAR_PER_LAP = 3.5

# Approximate fuel burn per lap (%)
FUEL_BURN_PER_LAP = 3.0

# Tyre condition restored after a pit stop
PIT_TYRE_RESTORE = 95.0

# Fuel added during a pit stop (partial refuel, simplified)
PIT_FUEL_RESTORE = 80.0

# Lap numbers where weather changes (lap → new weather)
WEATHER_EVENTS = {
    20: "light rain",
    30: "heavy rain",
    40: "overcast",
    50: "dry",
}


# ===========================================================
# Simulation helper functions
# ===========================================================

def _apply_pit_stop(state: RaceState) -> RaceState:
    """
    Returns a new RaceState after applying a pit stop.
    Tyres are restored and partial fuel is added.
    """
    return RaceState(
        current_lap=state.current_lap,
        total_laps=state.total_laps,
        position=min(state.position + 1, 20),  # Pit stop typically costs 1 position
        fuel=min(state.fuel + PIT_FUEL_RESTORE, 100.0),
        tyre_condition=PIT_TYRE_RESTORE,
        weather=state.weather,
        gap_ahead=state.gap_ahead + 5.0,   # Regain pace takes time
        gap_behind=max(0.5, state.gap_behind - 15.0),  # Pit exit is vulnerable
    )


def _next_lap_state(
    state: RaceState,
    decision: str,
    pit_stop_done: bool
) -> RaceState:
    """
    Computes the next lap's RaceState from the current one.

    Parameters
    ----------
    state        : Current lap state.
    decision     : Strategy decision for this lap.
    pit_stop_done: Whether a pit stop was executed this lap.

    Returns
    -------
    Updated RaceState for the following lap.
    """
    next_lap = state.current_lap + 1

    # --- Weather update ---
    new_weather = WEATHER_EVENTS.get(next_lap, state.weather)

    # --- Tyre wear ---
    if decision == "CONSERVE":
        wear_factor = 0.6   # Lift-and-coast reduces tyre wear
    elif decision == "ATTACK":
        wear_factor = 1.4   # Aggressive driving increases wear
    else:
        wear_factor = 1.0

    new_tyre = max(0.0, state.tyre_condition - (TYRE_WEAR_PER_LAP * wear_factor))

    # --- Fuel consumption ---
    if decision == "CONSERVE":
        fuel_factor = 0.7
    elif decision == "ATTACK":
        fuel_factor = 1.3
    else:
        fuel_factor = 1.0

    new_fuel = max(0.0, state.fuel - (FUEL_BURN_PER_LAP * fuel_factor))

    # --- Gap dynamics ---
    # Gap to car ahead shrinks slightly when attacking
    if decision == "ATTACK":
        new_gap_ahead = max(0.2, state.gap_ahead - 0.3)
    elif decision == "PIT":
        new_gap_ahead = state.gap_ahead + 5.0
    else:
        new_gap_ahead = min(state.gap_ahead + 0.5, 30.0)

    # Gap behind increases when defending or staying out
    if decision == "DEFEND":
        new_gap_behind = min(state.gap_behind + 0.8, 30.0)
    elif decision == "PIT":
        new_gap_behind = max(0.5, state.gap_behind - 20.0)
    else:
        new_gap_behind = min(state.gap_behind + 0.3, 30.0)

    # --- Position changes ---
    new_position = state.position
    if decision == "ATTACK" and state.gap_ahead <= 1.0 and state.position > 1:
        new_position = max(1, state.position - 1)   # Successful overtake
        new_gap_ahead = 3.0                          # Now ahead of that car

    return RaceState(
        current_lap=next_lap,
        total_laps=state.total_laps,
        position=new_position,
        fuel=new_fuel,
        tyre_condition=new_tyre,
        weather=new_weather,
        gap_ahead=new_gap_ahead,
        gap_behind=new_gap_behind,
    )


# ===========================================================
# Main simulation entry point
# ===========================================================

def run_simulation(total_laps: int = 60, delay: float = 0.4) -> None:
    """
    Runs a full simulated race from lap 1 to total_laps.

    Parameters
    ----------
    total_laps : Race length in laps (default 60).
    delay      : Pause in seconds between each lap display (default 0.4s).
    """
    print("\n" + "=" * 52)
    print(f"{BOLD}{CYAN}       🏁  RACE SIMULATION STARTING{RESET}")
    print(f"       Total Distance: {total_laps} Laps")
    print("=" * 52)
    print(f"\n  {YELLOW}Press Ctrl+C at any time to abort the simulation.{RESET}\n")
    time.sleep(1)

    # --- Initial race state (lap 1) ---
    state = RaceState(
        current_lap=1,
        total_laps=total_laps,
        position=5,
        fuel=100.0,
        tyre_condition=100.0,
        weather="dry",
        gap_ahead=3.0,
        gap_behind=4.0,
    )

    pit_count: int = 0
    decisions_log: list = []

    try:
        while state.current_lap <= state.total_laps:
            # Evaluate strategy for this lap
            result: StrategyResult = evaluate(state)
            decision = result.decision
            decisions_log.append((state.current_lap, decision))

            # Print lap summary
            _print_sim_lap(state, result)
            time.sleep(delay)

            # If we're on the final lap, stop
            if state.current_lap >= state.total_laps:
                break

            # Apply pit stop if recommended
            if decision == "PIT":
                state = _apply_pit_stop(state)
                pit_count += 1
                print(f"  {YELLOW}🔧 PIT STOP #{pit_count} — Tyres changed, fuel added.{RESET}")
                time.sleep(delay)
                decision = "STAY OUT"   # After pitting, default to stay out for next lap calc

            # Advance to next lap
            state = _next_lap_state(state, decision, pit_stop_done=(decision == "PIT"))

        # --- Race Over ---
        _print_race_summary(state, pit_count, decisions_log)

    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}⚠  Simulation aborted by user on lap {state.current_lap}.{RESET}\n")


def _print_sim_lap(state: RaceState, result: StrategyResult) -> None:
    """Prints a compact lap-by-lap simulation display."""
    colour_map = {
        "PIT": YELLOW, "STAY OUT": GREEN, "ATTACK": CYAN,
        "DEFEND": "\033[95m", "CONSERVE": "\033[91m",
    }
    col = colour_map.get(result.decision, "")
    end = RESET

    print(f"\n  {'─' * 48}")
    print(
        f"  Lap {state.current_lap:>3}/{state.total_laps}  |  "
        f"P{state.position:<2}  |  "
        f"⛽ {state.fuel:>5.1f}%  |  "
        f"🔵 Tyres {state.tyre_condition:>5.1f}%  |  "
        f"🌤  {state.weather.title():<12}"
    )
    print(
        f"  Gaps → Ahead: {state.gap_ahead:.1f}s  |  Behind: {state.gap_behind:.1f}s"
    )
    print(f"  {col}{BOLD}  ▶ DECISION: {result.decision}{end}")
    if result.reasons:
        print(f"    ↳ {result.reasons[0]}")


def _print_race_summary(
    state: RaceState,
    pit_count: int,
    log: list,
) -> None:
    """Prints a summary of the completed race simulation."""
    print("\n\n" + "=" * 52)
    print(f"{BOLD}{GREEN}       🏁  RACE SIMULATION COMPLETE{RESET}")
    print("=" * 52)
    print(f"  Final Position : P{state.position}")
    print(f"  Pit Stops Made : {pit_count}")
    print(f"  Final Fuel     : {state.fuel:.1f}%")
    print(f"  Final Tyres    : {state.tyre_condition:.1f}%")

    # Count decisions
    from collections import Counter
    counts = Counter(dec for _, dec in log)
    print("\n  Strategy decisions across the race:")
    for decision, count in counts.most_common():
        print(f"    {decision:<12} : {count} laps")
    print("=" * 52 + "\n")
