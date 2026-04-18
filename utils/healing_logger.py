"""
HealingLogger — Singleton event recorder for self-healing events.

Built by Claude Opus 4.7.

Every time SmartLocator repairs a broken locator, a HealingEvent is produced
here. The logger does three jobs at once:

    1. Emits a visually striking console banner so the recovery is *visible*
       while the test is running (important for the demo video).
    2. Attaches healing metadata + screenshot to the active Allure step so
       testers can see what happened in the final report.
    3. Accumulates every event so the HTML dashboard and the suggested_fixes
       markdown file can be generated at the end of the run.

The logger is intentionally a module-level singleton. Tests are usually run
serially within a process, and a global collector avoids threading context
through every page object.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional


def _safe_print(line: str) -> None:
    try:
        print(line)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "ascii"
        try:
            print(line.encode(enc, errors="replace").decode(enc, errors="replace"))
        except Exception:
            print(line.encode("ascii", errors="replace").decode("ascii"))


# ANSI colors — degrade gracefully when stdout isn't a TTY.
class _Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

    @classmethod
    def enabled(cls) -> bool:
        try:
            return sys.stdout.isatty()
        except Exception:
            return False


def _c(text: str, color: str) -> str:
    if _Ansi.enabled():
        return f"{color}{text}{_Ansi.RESET}"
    return text


@dataclass
class HealingEvent:
    """A single self-healing occurrence."""

    locator_name: str
    description: str
    original_strategy: str
    healed_strategy: str
    stage: str
    confidence: float
    timestamp: float
    screenshot_png: Optional[bytes] = None
    scenario_name: str = ""
    feature_name: str = ""


class HealingLogger:
    """Module-level singleton. Use the exported HEALING_LOGGER instance."""

    def __init__(self) -> None:
        self.events: List[HealingEvent] = []
        self._current_scenario: str = ""
        self._current_feature: str = ""
        self._run_started_at: float = time.time()

    # --------------------------------------------------------------- lifecycle

    def bind_scenario(self, feature_name: str, scenario_name: str) -> None:
        """Called from environment.py before each scenario."""
        self._current_feature = feature_name
        self._current_scenario = scenario_name

    def reset(self) -> None:
        """Clear state at the start of a fresh run."""
        self.events.clear()
        self._run_started_at = time.time()

    # ------------------------------------------------------------------ record

    def record(self, event: HealingEvent) -> None:
        """Record a healing event and broadcast it to console + Allure + live dashboard."""
        event.scenario_name = self._current_scenario
        event.feature_name = self._current_feature
        self.events.append(event)

        self._emit_console(event)
        self._emit_allure(event)
        self._emit_live(event)

    # ------------------------------------------------------------------ output

    def _emit_console(self, e: HealingEvent) -> None:
        badge = _c(" SELF-HEAL ", _Ansi.BOLD + _Ansi.GREEN)
        confidence_pct = f"{e.confidence * 100:.0f}%"
        confidence_color = (
            _Ansi.GREEN if e.confidence >= 0.8
            else _Ansi.YELLOW if e.confidence >= 0.65
            else _Ansi.RED
        )

        print("")
        _safe_print(_c("  ┌" + "─" * 72 + "┐", _Ansi.CYAN))
        _safe_print(_c("  │", _Ansi.CYAN) + f" {badge} {_c(e.locator_name, _Ansi.BOLD)}")
        _safe_print(_c("  │", _Ansi.CYAN) + _c(f"   stage       :", _Ansi.DIM) + f" {e.stage}")
        _safe_print(_c("  │", _Ansi.CYAN) + _c(f"   original    :", _Ansi.DIM) + _c(f" {e.original_strategy}", _Ansi.RED))
        _safe_print(_c("  │", _Ansi.CYAN) + _c(f"   healed with :", _Ansi.DIM) + _c(f" {e.healed_strategy}", _Ansi.GREEN))
        _safe_print(_c("  │", _Ansi.CYAN) + _c(f"   confidence  :", _Ansi.DIM) + _c(f" {confidence_pct}", confidence_color))
        if e.description:
            _safe_print(_c("  │", _Ansi.CYAN) + _c(f"   description :", _Ansi.DIM) + f" {e.description}")
        _safe_print(_c("  └" + "─" * 72 + "┘", _Ansi.CYAN))
        print("")
        sys.stdout.flush()

    def _emit_allure(self, e: HealingEvent) -> None:
        """Attach healing details to the current Allure step, if available."""
        try:
            import allure
        except ImportError:
            return

        report = (
            f"SELF-HEALING LOCATOR\n"
            f"====================\n\n"
            f"Locator name : {e.locator_name}\n"
            f"Description  : {e.description}\n"
            f"Stage        : {e.stage}\n"
            f"Confidence   : {e.confidence * 100:.0f}%\n\n"
            f"Original locator : {e.original_strategy}\n"
            f"Healed locator   : {e.healed_strategy}\n"
        )

        try:
            allure.attach(
                report,
                name=f"HEALED: {e.locator_name}",
                attachment_type=allure.attachment_type.TEXT,
            )
            if e.screenshot_png:
                allure.attach(
                    e.screenshot_png,
                    name=f"HEAL_SCREENSHOT: {e.locator_name}",
                    attachment_type=allure.attachment_type.PNG,
                )
        except Exception:
            # Allure context isn't active (e.g. running outside a step) —
            # healing still recorded in memory for the dashboard.
            pass

    def _emit_live(self, e: HealingEvent) -> None:
        """Mirror the heal to the live WebSocket dashboard if it's running."""
        try:
            from utils.live_dashboard import LIVE
            LIVE.heal({
                "locator_name": e.locator_name,
                "description": e.description,
                "original_strategy": e.original_strategy,
                "healed_strategy": e.healed_strategy,
                "stage": e.stage,
                "confidence": e.confidence,
                "scenario_name": e.scenario_name,
                "feature_name": e.feature_name,
                "timestamp": e.timestamp,
            })
        except Exception:
            pass

    # ------------------------------------------------------------------ stats

    def total_count(self) -> int:
        return len(self.events)

    def avg_confidence(self) -> float:
        if not self.events:
            return 0.0
        return sum(e.confidence for e in self.events) / len(self.events)

    def events_by_stage(self) -> dict:
        buckets: dict = {}
        for e in self.events:
            buckets.setdefault(e.stage, []).append(e)
        return buckets


HEALING_LOGGER = HealingLogger()
