"""
Behave environment hooks.

Extended by Claude Opus 4.7 with:

  * Self-healing lifecycle (HEALING_LOGGER reset, dashboard generation)
  * Real-time live execution dashboard (Flask-SocketIO) — opens a browser
    tab automatically and streams every feature / scenario / step + heal
    event as it happens.

Disable the live dashboard in CI or when unwanted by exporting
`LIVE_DASHBOARD=0`. The CI env var also disables it automatically.
"""

import time

from utils.driver_factory import get_driver
from utils.allure_utils import attach_screenshot
from utils.healing_logger import HEALING_LOGGER
from utils.healing_report import generate_all as generate_healing_report
from utils.live_dashboard import LIVE


def _count_scenarios(context) -> int:
    """Best-effort scenario count across all features for the progress bar."""
    try:
        total = 0
        for feature in context._runner.features:
            for scenario in feature.scenarios:
                # Behave expands a Scenario Outline into .scenarios at runtime.
                if hasattr(scenario, "scenarios") and scenario.scenarios:
                    total += len(scenario.scenarios)
                else:
                    total += 1
        return total
    except Exception:
        return 0


def before_all(context):
    context.browser = "chrome"
    HEALING_LOGGER.reset()

    # Boot the live dashboard server + browser tab.
    LIVE.start()
    total = _count_scenarios(context)
    LIVE.run_start(total_scenarios=total)

    _banner = [
        "",
        "  +==============================================================+",
        "  |  SELF-HEALING TEST FRAMEWORK . engineered by Claude Opus 4.7 |",
        "  |  Watch for SELF-HEAL banners during the run.                 |",
        "  +==============================================================+",
        "",
    ]
    for line in _banner:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))

    # Give the dashboard tab a moment to open and connect before tests start.
    if LIVE.enabled:
        time.sleep(1.5)


def before_feature(context, feature):
    LIVE.feature_start(feature.name)


def after_feature(context, feature):
    LIVE.feature_end(feature.name, feature.status.name if hasattr(feature.status, "name") else str(feature.status))


def before_scenario(context, scenario):
    context.driver = get_driver(browser=context.browser)
    context.driver.implicitly_wait(10)
    HEALING_LOGGER.bind_scenario(
        feature_name=scenario.feature.name if scenario.feature else "",
        scenario_name=scenario.name,
    )
    context._scenario_started_at = time.time()
    LIVE.scenario_start(
        name=scenario.name,
        tags=list(scenario.tags or []),
        feature=scenario.feature.name if scenario.feature else "",
    )


def after_scenario(context, scenario):
    if scenario.status == "failed":
        attach_screenshot(context.driver, f"FAILED: {scenario.name}")
    if hasattr(context, "driver"):
        context.driver.quit()

    duration = time.time() - getattr(context, "_scenario_started_at", time.time())
    status_name = scenario.status.name if hasattr(scenario.status, "name") else str(scenario.status)
    LIVE.scenario_end(name=scenario.name, status=status_name, duration_s=duration)


def before_step(context, step):
    context._step_started_at = time.time()
    LIVE.step_start(keyword=step.keyword, name=step.name)


def after_step(context, step):
    duration = time.time() - getattr(context, "_step_started_at", time.time())
    status_name = step.status.name if hasattr(step.status, "name") else str(step.status)
    LIVE.step_end(
        keyword=step.keyword,
        name=step.name,
        status=status_name,
        duration_s=duration,
    )


def after_all(context):
    total = HEALING_LOGGER.total_count()
    if total:
        avg = HEALING_LOGGER.avg_confidence() * 100
        print("")
        print(f"  Self-healing summary: {total} locator(s) auto-repaired "
              f"(avg confidence {avg:.0f}%)")
    else:
        print("")
        print("  Self-healing summary: 0 repairs — all locators resolved cleanly.")

    generate_healing_report()

    LIVE.run_end()
    # Keep the server alive briefly so the browser receives the run.end frame
    # and shows the completion overlay before we exit the process.
    if LIVE.enabled:
        time.sleep(2.0)
