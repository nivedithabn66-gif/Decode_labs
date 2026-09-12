"""
race_state.py
-------------
Defines the RaceState data structure that captures all current
race conditions observed by the AI Racing Strategy Agent.

This module is purely a data container — no logic lives here.
"""

from dataclasses import dataclass
from typing import Literal

# Valid weather options understood by the strategy engine
VALID_WEATHER = ("dry", "light rain", "heavy rain", "overcast")

WeatherType = Literal["dry", "light rain", "heavy rain", "overcast"]


@dataclass
class RaceState:
    """
    Encapsulates a complete snapshot of the current race situation.

    Attributes
    ----------
    current_lap       : The lap the car is currently on.
    total_laps        : The total number of laps in the race.
    position          : Current finishing position (1 = leader).
    fuel              : Remaining fuel expressed as a percentage (0–100).
    tyre_condition    : Tyre health expressed as a percentage (0–100).
    weather           : Track weather condition string.
    gap_ahead         : Gap in seconds to the car directly ahead (0 if leader).
    gap_behind        : Gap in seconds to the car directly behind (very large
                        number if no car behind).
    """

    current_lap: int
    total_laps: int
    position: int
    fuel: float
    tyre_condition: float
    weather: WeatherType
    gap_ahead: float
    gap_behind: float

    # ------------------------------------------------------------------
    # Derived / convenience properties
    # ------------------------------------------------------------------

    @property
    def remaining_laps(self) -> int:
        """Number of laps still to run (inclusive of current lap)."""
        return max(0, self.total_laps - self.current_lap)

    @property
    def race_progress(self) -> float:
        """Race completion ratio between 0.0 (start) and 1.0 (finish)."""
        if self.total_laps == 0:
            return 0.0
        return self.current_lap / self.total_laps

    @property
    def is_raining(self) -> bool:
        """True when the weather involves any form of rain."""
        return "rain" in self.weather.lower()

    def __str__(self) -> str:
        """Human-readable race condition summary for terminal display."""
        lines = [
            "=" * 50,
            "         🏎️  CURRENT RACE CONDITIONS",
            "=" * 50,
            f"  Lap            : {self.current_lap} / {self.total_laps}",
            f"  Remaining Laps : {self.remaining_laps}",
            f"  Position       : P{self.position}",
            f"  Fuel           : {self.fuel:.1f}%",
            f"  Tyre Condition : {self.tyre_condition:.1f}%",
            f"  Weather        : {self.weather.title()}",
            f"  Gap Ahead      : {self.gap_ahead:.2f} sec",
            f"  Gap Behind     : {self.gap_behind:.2f} sec",
            "=" * 50,
        ]
        return "\n".join(lines)
