# 🏎️ AI Racing Strategy Agent

**DecodeLabs — Artificial Intelligence Project 1**

---

## Description

The **AI Racing Strategy Agent** is a rule-based intelligent system that acts as a Formula 1-style race strategist. It observes simulated race conditions (tyres, fuel, weather, gaps, lap count), evaluates them through a priority-based rule engine, and recommends the best racing strategy — with a clear explanation of *why* it made that decision.

This project demonstrates the foundations of **Artificial Intelligence through rule-based reasoning**, without using any machine learning, external APIs, or complex dependencies.

---

## Features

| Feature | Description |
|---|---|
| 🧠 Rule-Based AI Engine | Prioritised `if/elif/else` decision logic |
| 💬 Natural Interaction | Responds to greetings and exit commands |
| 📊 Race Situation Analysis | Fully validated user input for 8 race parameters |
| 🏁 Race Simulation Mode | Lap-by-lap simulation over a full race distance |
| 📋 Explainable Decisions | Every decision includes reasons and action guidance |
| 🎨 Colour-Coded Output | ANSI-coloured terminal display |
| ✅ Input Validation | Handles all invalid input gracefully |

---

## AI Concept

The agent follows a classic AI agent loop:

```
Observe → Evaluate → Decide → Explain → Next State
```

```
┌─────────────────────────────────────────────────────────┐
│                   RACE CONDITIONS                        │
│  Lap | Position | Fuel% | Tyre% | Weather | Gaps        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                RULE EVALUATION ENGINE                    │
│  Priority 1: Critical Tyre?      → PIT                  │
│  Priority 2: Tyre low + many laps? → PIT                │
│  Priority 3: Weather changed?    → PIT                  │
│  Priority 4: Fuel critical?      → CONSERVE             │
│  Priority 5: Fuel low + top 5?   → CONSERVE             │
│  Priority 6: DRS opportunity?    → ATTACK               │
│  Priority 7: Under threat?       → DEFEND               │
│  Priority 8: All healthy?        → STAY OUT             │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│               STRATEGY DECISION + EXPLANATION            │
│  Decision: PIT                                          │
│  Reasons:  ✓ Tyres at 15% — risk of failure            │
│            ✓ Gap behind is 25 sec — safe to pit        │
│  Action:   Box this lap, switch tyre compound           │
└─────────────────────────────────────────────────────────┘
```

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| `if / elif / else` | Rule-based decision logic |
| `dataclasses` | Clean data structures (RaceState, StrategyResult) |
| Functions & modules | Modular, single-responsibility design |
| Loops | Continuous interaction and simulation |
| Input validation | Robust user input handling |
| ANSI escape codes | Colour-coded terminal output |

> **No machine learning. No external APIs. No pip packages.**

---

## How It Works — Rule Engine Explained

The `strategy_engine.py` evaluates rules in strict **priority order**. The first rule that fires determines the decision. This prevents contradictory recommendations.

### Example: PIT Decision

```python
# Rule: Critical tyre condition
if tyre_condition < 20:
    → PIT  (Reason: "Tyre condition critically low — risk of failure")

# Rule: Degraded tyres with many laps left
if tyre_condition < 40 AND remaining_laps > 15:
    → PIT  (Reason: "Tyres won't last to the end")
```

### Example: ATTACK Decision

```python
# Rule: DRS overtaking opportunity
if gap_ahead <= 1.0 AND tyre_condition >= 50 AND fuel >= 30:
    → ATTACK  (Reasons: "Within DRS range", "Tyres healthy", "Fuel sufficient")
```

### Example: CONSERVE Decision

```python
# Rule: Critical fuel level
if fuel < (remaining_laps * 3.0) AND fuel < 30:
    → CONSERVE  (Reason: "Estimated fuel deficit for remaining laps")
```

---

## Project Structure

```
ai-racing-strategy-agent/
│
├── main.py             ← Entry point, interaction loop, menu routing
├── race_state.py       ← RaceState dataclass (all race inputs)
├── strategy_engine.py  ← Priority-based rule evaluation engine
├── rules.py            ← Individual rule functions (each independently testable)
├── simulator.py        ← Lap-by-lap race simulation
├── utils.py            ← Input validation, display helpers
├── requirements.txt    ← No external packages required
└── README.md           ← This file
```

---

## Installation

### Prerequisites

- Python 3.8 or higher installed
- VS Code (recommended) or any terminal

### Steps

1. **Clone or download** the project folder.

2. **Open a terminal** in VS Code:
   ```
   View → Terminal  (or press Ctrl + `)
   ```

3. **Navigate to the project directory**:
   ```powershell
   cd "c:\Users\Niveditha B N\OneDrive\Documents\Niveditha B N\Decodelabs\Project1"
   ```

4. **Verify Python is available**:
   ```powershell
   python --version
   ```

---

## Running the Project

```powershell
python main.py
```

> No `pip install` is required. The project uses only Python standard library modules.

---

## Example Session

```
====================================================
        🏎️  AI RACING STRATEGY AGENT
====================================================
  Rule-Based AI | DecodeLabs — Project 1
====================================================

────────────────────────────────────────────────────
  What would you like to do?
────────────────────────────────────────────────────
  1. Analyse a race situation
  2. Run a race simulation (60 laps)
  3. Exit
────────────────────────────────────────────────────
  Enter choice: 1

  📋  Enter Current Race Conditions
  ────────────────────────────────────────────────────
  Total laps in race          : 60
  Current lap                 : 42
  Current position (1 = lead) : 4
  Fuel remaining (%)          : 27
  Tyre condition (%)          : 18
  Weather options             : dry | light rain | heavy rain | overcast
  Weather condition           : light rain
  Gap to car ahead (seconds)  : 2.0
  Gap to car behind (seconds) : 25.0

====================================================
         CURRENT RACE CONDITIONS
====================================================
  Lap            : 42 / 60
  Remaining Laps : 18
  Position       : P4
  Fuel           : 27.0%
  Tyre Condition : 18.0%
  Weather        : Light Rain
  Gap Ahead      : 2.00 sec
  Gap Behind     : 25.00 sec
====================================================

====================================================
              🧠  AI DECISION
====================================================

  ⬤  STRATEGY: PIT

  Reasons:
    ✓ Tyre condition is critically low (18.0%) — risk of failure
    ✓ Gap behind (25.0 sec) is large enough for a safe pit stop
    ✓ 18 laps remaining

  Recommended Action:
    → Box this lap. Switch to a suitable tyre compound and resume racing
      at full pace as quickly as possible.
====================================================
```

---

## Strategy Decisions

| Decision | When It Fires |
|---|---|
| **PIT** | Tyres < 20%, or tyres < 40% with 15+ laps left, or rain detected |
| **CONSERVE** | Fuel below threshold for remaining laps, or fuel < 25% in top 5 |
| **ATTACK** | Gap ahead ≤ 1.0s, tyres ≥ 50%, fuel ≥ 30%, not P1 |
| **DEFEND** | Gap behind ≤ 1.0s and tyres < 50%, or low fuel in points position |
| **STAY OUT** | Tyres ≥ 50%, fuel ≥ 30%, dry weather, no immediate threat |

---

## Input Validation

All inputs are validated before analysis:

| Input | Validation |
|---|---|
| Total / current lap | Integer, 1–300, current ≤ total |
| Position | Integer, 1–20 |
| Fuel % | Float, 0.0–100.0 |
| Tyre condition % | Float, 0.0–100.0 |
| Weather | Must match: dry, light rain, heavy rain, overcast |
| Gaps (seconds) | Float, 0.0–300.0 |

Invalid input triggers a clear error message and re-prompts the user. The application never crashes on bad input.

---

## Future Improvements

> **Note:** The following improvements are planned for future versions and are NOT part of the current Project 1 implementation.

| Future Feature | Description |
|---|---|
| 🤖 Machine Learning | Train a model on historical F1 race data to predict optimal strategies |
| 🔄 Reinforcement Learning | Agent learns optimal strategies through race simulation rewards |
| 📊 Data Collection | Log race states and decisions to build a training dataset |
| 📈 Visualisation Dashboard | Real-time strategy dashboard using Streamlit or Plotly |
| 🏎️ Real Racing Data | Integrate with Formula 1 open datasets (FastF1 library) |
| 🌐 Web Interface | Browser-based interface for the strategy agent |
| 🎮 Advanced Simulation | More realistic tyre degradation curves and fuel models |

---

## Author

**Niveditha B N**  
DecodeLabs — AI Project 1  
Rule-Based AI Racing Strategy Agent

---

*Built with Python standard library only. No machine learning. No APIs. Pure rule-based AI.*
