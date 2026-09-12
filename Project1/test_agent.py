# -*- coding: utf-8 -*-
"""
test_agent.py
-------------
Automated tests for the AI Racing Strategy Agent.
Run this file to verify all decisions and basic logic.

Usage:
    python test_agent.py
"""

import sys
sys.path.insert(0, r'c:\Users\Niveditha B N\OneDrive\Documents\Niveditha B N\Decodelabs\Project1')

from race_state import RaceState
from strategy_engine import evaluate


def run_test(label: str, state: RaceState, expected: str) -> bool:
    """Runs a single decision test and prints the result."""
    result = evaluate(state)
    passed = result.decision == expected
    status = "PASS" if passed else "FAIL"
    first_reason = result.reasons[0] if result.reasons else "no reason"
    print(f"  [{status}] {label}")
    print(f"         Decision : {result.decision}  (expected {expected})")
    print(f"         Reason   : {first_reason}")
    print()
    return passed


def main():
    print("=" * 58)
    print("     AI RACING STRATEGY AGENT — AUTOMATED TESTS")
    print("=" * 58 + "\n")

    results = []

    # ----------------------------------------------------------
    # PIT decisions
    # ----------------------------------------------------------
    results.append(run_test(
        "PIT | Critical tyre condition (15%)",
        RaceState(30, 60, 5, 70, 15, "dry", 3.0, 25.0),
        "PIT"
    ))

    results.append(run_test(
        "PIT | Low tyres (35%) with 20 laps remaining",
        RaceState(40, 60, 4, 60, 35, "dry", 2.5, 8.0),
        "PIT"
    ))

    results.append(run_test(
        "PIT | Rain detected, tyre switch required",
        RaceState(20, 60, 3, 75, 60, "light rain", 4.0, 30.0),
        "PIT"
    ))

    # ----------------------------------------------------------
    # CONSERVE decisions
    # ----------------------------------------------------------
    results.append(run_test(
        "CONSERVE | Fuel critically low for remaining laps",
        RaceState(50, 60, 3, 15, 70, "dry", 2.0, 5.0),
        "CONSERVE"
    ))

    results.append(run_test(
        "CONSERVE | Fuel 22% in P3 with safe gap behind",
        RaceState(45, 60, 3, 22, 80, "dry", 3.0, 10.0),
        "CONSERVE"
    ))

    # ----------------------------------------------------------
    # ATTACK decisions
    # ----------------------------------------------------------
    results.append(run_test(
        "ATTACK | Gap 0.8s, tyres 65%, fuel 40%, P4",
        RaceState(35, 60, 4, 40, 65, "dry", 0.8, 5.0),
        "ATTACK"
    ))

    results.append(run_test(
        "ATTACK | Final 3 laps, gap 1.5s, P5",
        RaceState(57, 60, 5, 35, 55, "dry", 1.5, 8.0),
        "ATTACK"
    ))

    # ----------------------------------------------------------
    # DEFEND decisions
    # ----------------------------------------------------------
    results.append(run_test(
        "DEFEND | Car behind 0.7s, tyres worn (40%)",
        RaceState(40, 60, 5, 45, 40, "dry", 5.0, 0.7),
        "DEFEND"
    ))

    # ----------------------------------------------------------
    # STAY OUT decisions
    # ----------------------------------------------------------
    results.append(run_test(
        "STAY OUT | Tyres 80%, fuel 60%, dry, safe gaps",
        RaceState(20, 60, 3, 60, 80, "dry", 4.0, 8.0),
        "STAY OUT"
    ))

    # ----------------------------------------------------------
    # Keyword constants
    # ----------------------------------------------------------
    from main import GREETING_WORDS, EXIT_WORDS
    greet_ok = all(w in GREETING_WORDS for w in ["hi", "hello", "hey"])
    exit_ok = all(w in EXIT_WORDS for w in ["bye", "exit", "quit"])

    status_g = "PASS" if greet_ok else "FAIL"
    status_e = "PASS" if exit_ok else "FAIL"
    print(f"  [{status_g}] Greeting keywords: {sorted(GREETING_WORDS)}")
    print(f"  [{status_e}] Exit keywords    : {sorted(EXIT_WORDS)}")
    print()
    results.extend([greet_ok, exit_ok])

    # ----------------------------------------------------------
    # RaceState derived properties
    # ----------------------------------------------------------
    state = RaceState(42, 60, 4, 27, 18, "light rain", 2.0, 25.0)
    rem_ok = state.remaining_laps == 18
    rain_ok = state.is_raining is True
    prog_ok = abs(state.race_progress - 42/60) < 0.001

    status_r = "PASS" if rem_ok else "FAIL"
    status_rn = "PASS" if rain_ok else "FAIL"
    status_p = "PASS" if prog_ok else "FAIL"
    print(f"  [{status_r}]  RaceState.remaining_laps = {state.remaining_laps}  (expected 18)")
    print(f"  [{status_rn}]  RaceState.is_raining = {state.is_raining}  (expected True)")
    print(f"  [{status_p}]  RaceState.race_progress = {state.race_progress:.3f}  (expected 0.700)")
    print()
    results.extend([rem_ok, rain_ok, prog_ok])

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------
    passed = sum(1 for r in results if r)
    total = len(results)
    bar = "=" * 58
    print(bar)
    if passed == total:
        print(f"  [OK]  ALL {total}/{total} TESTS PASSED -- Agent is working correctly!")
    else:
        print(f"  [!!] {passed}/{total} tests passed -- check FAIL entries above.")
    print(bar)


if __name__ == "__main__":
    main()
