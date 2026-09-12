"""
utils.py
--------
Utility functions for the AI Racing Strategy Agent.

Responsibilities:
  - Validated input prompts (float, int, weather)
  - Terminal display helpers (headers, dividers)
  - Colour-coded decision banners

No racing logic lives here — only I/O and formatting helpers.
"""

from race_state import VALID_WEATHER, RaceState

# ANSI colour codes (work on Windows 10+ and most terminals)
RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
WHITE   = "\033[97m"

# Decision → colour mapping
DECISION_COLOURS = {
    "PIT":       YELLOW,
    "STAY OUT":  GREEN,
    "ATTACK":    CYAN,
    "DEFEND":    MAGENTA,
    "CONSERVE":  RED,
}


# ------------------------------------------------------------------
# Display helpers
# ------------------------------------------------------------------

def print_header() -> None:
    """Prints the application header banner."""
    print("\n" + "=" * 52)
    print(f"{BOLD}        🏎️  AI RACING STRATEGY AGENT{RESET}")
    print("=" * 52)
    print("  Rule-Based AI | DecodeLabs — Project 1")
    print("=" * 52)


def print_divider() -> None:
    """Prints a simple horizontal divider."""
    print("-" * 52)


def print_decision(decision: str, reasons: list, recommendation: str) -> None:
    """
    Prints a formatted, colour-coded strategy decision block.

    Parameters
    ----------
    decision       : The strategy keyword (PIT, ATTACK, etc.)
    reasons        : List of reason strings that triggered the decision.
    recommendation : A plain-English action summary.
    """
    colour = DECISION_COLOURS.get(decision, WHITE)
    print("\n" + "=" * 52)
    print(f"              🧠  AI DECISION")
    print("=" * 52)
    print(f"\n  {colour}{BOLD}⬤  STRATEGY: {decision}{RESET}\n")
    print(f"  {'Reasons:':}")
    for reason in reasons:
        print(f"    ✓ {reason}")
    print()
    print(f"  {'Recommended Action:'}")
    print(f"    → {recommendation}")
    print("\n" + "=" * 52)


# ------------------------------------------------------------------
# Validated input helpers
# ------------------------------------------------------------------

def input_float(prompt: str, min_val: float = 0.0, max_val: float = float("inf")) -> float:
    """
    Prompts the user for a floating-point number within [min_val, max_val].
    Repeats until valid input is provided.

    Parameters
    ----------
    prompt  : The question to display to the user.
    min_val : Minimum acceptable value (inclusive).
    max_val : Maximum acceptable value (inclusive).

    Returns
    -------
    A valid float within the specified range.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print(f"  ⚠  Please enter a valid number (e.g. 45.5).")
            continue

        if value < min_val or value > max_val:
            print(f"  ⚠  Value must be between {min_val} and {max_val}. Got: {value}")
            continue

        return value


def input_int(prompt: str, min_val: int = 1, max_val: int = 10_000) -> int:
    """
    Prompts the user for an integer within [min_val, max_val].
    Repeats until valid input is provided.

    Parameters
    ----------
    prompt  : The question to display to the user.
    min_val : Minimum acceptable value (inclusive).
    max_val : Maximum acceptable value (inclusive).

    Returns
    -------
    A valid integer within the specified range.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"  ⚠  Please enter a whole number (e.g. 3).")
            continue

        if value < min_val or value > max_val:
            print(f"  ⚠  Value must be between {min_val} and {max_val}. Got: {value}")
            continue

        return value


def input_weather(prompt: str) -> str:
    """
    Prompts the user for a valid weather condition.
    Accepts case-insensitive input and normalises to lowercase.

    Valid options: dry | light rain | heavy rain | overcast

    Returns
    -------
    A lowercase validated weather string.
    """
    valid_display = " | ".join(VALID_WEATHER)
    while True:
        raw = input(prompt).strip().lower()
        if raw in VALID_WEATHER:
            return raw
        print(f"  ⚠  Invalid weather. Choose from: {valid_display}")


def collect_race_state() -> RaceState:
    """
    Interactively collects all race condition inputs from the user
    and returns a validated RaceState object.

    Cross-field validations:
      - current_lap must not exceed total_laps.
    """
    print("\n  📋  Enter Current Race Conditions")
    print_divider()

    total_laps = input_int(
        "  Total laps in race          : ",
        min_val=1, max_val=300
    )
    current_lap = input_int(
        "  Current lap                 : ",
        min_val=1, max_val=total_laps
    )

    # Current lap cross-validation
    if current_lap > total_laps:
        print(f"  ⚠  Current lap ({current_lap}) cannot exceed total laps ({total_laps}).")
        current_lap = total_laps

    position = input_int(
        "  Current position (1 = lead) : ",
        min_val=1, max_val=20
    )
    fuel = input_float(
        "  Fuel remaining (%)          : ",
        min_val=0.0, max_val=100.0
    )
    tyre_condition = input_float(
        "  Tyre condition (%)          : ",
        min_val=0.0, max_val=100.0
    )

    valid_display = " | ".join(VALID_WEATHER)
    print(f"  Weather options             : {valid_display}")
    weather = input_weather(
        "  Weather condition           : "
    )
    gap_ahead = input_float(
        "  Gap to car ahead (seconds)  : ",
        min_val=0.0, max_val=300.0
    )
    gap_behind = input_float(
        "  Gap to car behind (seconds) : ",
        min_val=0.0, max_val=300.0
    )

    return RaceState(
        current_lap=current_lap,
        total_laps=total_laps,
        position=position,
        fuel=fuel,
        tyre_condition=tyre_condition,
        weather=weather,
        gap_ahead=gap_ahead,
        gap_behind=gap_behind,
    )
