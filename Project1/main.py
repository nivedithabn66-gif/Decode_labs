"""
main.py
-------
Entry point for the AI Racing Strategy Agent.

This module handles:
  - Application startup and greeting
  - The main interaction loop
  - Routing between analysis mode and simulation mode
  - Graceful exit

The agent responds to:
  • hi / hello / hey      → greeting
  • bye / exit / quit     → graceful shutdown
  • Menu choice 1         → manual race analysis
  • Menu choice 2         → automated race simulation
  • Menu choice 3         → exit

Usage
-----
    python main.py
"""

import sys
import io

# Force UTF-8 output on Windows (handles emoji and Unicode characters)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from utils import (
    print_header,
    print_divider,
    print_decision,
    collect_race_state,
    BOLD,
    RESET,
    CYAN,
    GREEN,
    YELLOW,
)
from strategy_engine import evaluate
from simulator import run_simulation


# ===========================================================
# Greeting keywords
# ===========================================================
GREETING_WORDS = {"hi", "hello", "hey", "hii", "helo"}
EXIT_WORDS     = {"bye", "exit", "quit", "goodbye", "q"}


# ===========================================================
# Greeting handler
# ===========================================================

def handle_greeting() -> None:
    """Prints a friendly introduction to the agent."""
    print("\n" + "=" * 52)
    print(f"  🏎️  {BOLD}Hello! I'm your AI Racing Strategy Agent.{RESET}")
    print("=" * 52)
    print(
        "\n  I observe race conditions and recommend the best\n"
        "  strategy using a rule-based decision engine.\n"
        "\n  What I can do:"
        "\n    ✓ Analyse any race situation and explain my reasoning"
        "\n    ✓ Run a full simulated race lap by lap"
        "\n    ✓ Recommend: PIT | STAY OUT | ATTACK | DEFEND | CONSERVE\n"
    )


# ===========================================================
# Main menu
# ===========================================================

def show_menu() -> None:
    """Displays the main options menu."""
    print("\n" + "─" * 52)
    print(f"  {BOLD}What would you like to do?{RESET}")
    print("─" * 52)
    print("  1. Analyse a race situation")
    print("  2. Run a race simulation (60 laps)")
    print("  3. Exit")
    print("─" * 52)


def get_menu_choice() -> str:
    """
    Reads the user's menu choice.
    Returns the raw stripped string for flexible matching.
    """
    return input("  Enter choice (1/2/3 or hi/bye): ").strip().lower()


# ===========================================================
# Race analysis mode
# ===========================================================

def run_analysis_mode() -> None:
    """
    Collects race conditions from the user, runs the strategy
    engine, and displays the formatted decision with explanations.
    """
    print("\n" + "=" * 52)
    print(f"  {CYAN}{BOLD}📊  RACE SITUATION ANALYSIS{RESET}")
    print("=" * 52)

    state = collect_race_state()

    print("\n" + state.__str__())

    result = evaluate(state)
    print_decision(
        decision=result.decision,
        reasons=result.reasons,
        recommendation=result.recommendation,
    )


# ===========================================================
# Main loop
# ===========================================================

def main() -> None:
    """
    Application entry point.
    Starts the interaction loop and routes user input to the
    appropriate handler.
    """
    print_header()
    print(
        "\n  Type 'hi' to get started, 'bye' to exit,\n"
        "  or choose from the menu below.\n"
    )

    while True:
        show_menu()
        choice = get_menu_choice()

        # ── Greeting ─────────────────────────────────────────
        if choice in GREETING_WORDS:
            handle_greeting()
            continue

        # ── Exit ──────────────────────────────────────────────
        if choice in EXIT_WORDS or choice == "3":
            print("\n" + "=" * 52)
            print(f"  🏁  {BOLD}Thanks for using AI Racing Strategy Agent!{RESET}")
            print("  Good luck on the track. Drive fast, think smart.")
            print("=" * 52 + "\n")
            sys.exit(0)

        # ── Race Analysis ─────────────────────────────────────
        elif choice == "1":
            try:
                run_analysis_mode()
            except KeyboardInterrupt:
                print(f"\n  {YELLOW}⚠  Analysis cancelled.{RESET}")

        # ── Race Simulation ───────────────────────────────────
        elif choice == "2":
            try:
                run_simulation(total_laps=60, delay=0.3)
            except KeyboardInterrupt:
                print(f"\n  {YELLOW}⚠  Simulation cancelled.{RESET}")

        # ── Unknown Input ─────────────────────────────────────
        else:
            print(f"\n  ⚠  '{choice}' is not a valid choice.")
            print("     Please enter 1, 2, 3, 'hi', or 'bye'.")


# ===========================================================
# Script entry guard
# ===========================================================

if __name__ == "__main__":
    main()
