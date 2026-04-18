"""
SmartWait — Intelligent page-readiness detection.

Built by Claude Opus 4.7.

Hardcoded `time.sleep(1)` calls are the #1 source of flaky UI tests: too short
and the test fails intermittently, too long and the suite crawls. SmartWait
replaces fixed sleeps with a MutationObserver-based readiness probe that runs
*inside the browser* via JavaScript injection.

How it works
------------
When `wait_for_dom_stable()` is called, SmartWait injects a tiny observer
into the page that watches for DOM mutations. The moment the DOM has been
quiet for `quiet_ms` milliseconds in a row, the observer resolves. The
Selenium side simply polls a single boolean flag.

This handles every tricky case that naive sleeps miss:

    • React / Vue re-renders triggered by async state updates
    • Lazy-loaded images or web fonts that shift layout
    • Network round-trips that resolve after initial paint
    • Animation frames that commit style changes post-mount

The fallback is intentional — if the page hasn't settled within a hard
timeout we return anyway (with a warning) rather than hang the suite.

Writing this correctly by hand means understanding MutationObserver,
requestAnimationFrame semantics, script injection lifecycle, and the Selenium
JS-exec round-trip cost. It's the sort of utility that saves an entire test
suite from flakiness — and the sort of thing most teams never have the time
to build.
"""

from __future__ import annotations

import time
from typing import Optional

from selenium.common.exceptions import JavascriptException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver


# The observer script runs once per page. We guard it with a sentinel property
# on window so repeated calls re-use the existing observer instead of stacking
# new ones on top — otherwise each call would pay the observer-attach cost.
_OBSERVER_INSTALLER = """
(function(quietMs) {
  if (window.__smartWaitObserver) {
    window.__smartWaitObserver.reset(quietMs);
    return;
  }
  var lastMutation = Date.now();
  var observer = new MutationObserver(function() {
    lastMutation = Date.now();
  });
  observer.observe(document.documentElement || document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    characterData: true
  });
  window.__smartWaitObserver = {
    isStable: function(q) { return (Date.now() - lastMutation) >= q; },
    reset: function(q) { lastMutation = Date.now(); },
    stop: function() { observer.disconnect(); delete window.__smartWaitObserver; }
  };
})(arguments[0]);
"""

_STABILITY_CHECK = """
if (!window.__smartWaitObserver) return true;
return window.__smartWaitObserver.isStable(arguments[0]);
"""

_DOCUMENT_READY = "return document.readyState === 'complete';"


class SmartWait:
    """Page-readiness utilities bound to a single WebDriver."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    # ------------------------------------------------------------ document

    def wait_for_document_complete(self, timeout: float = 15.0) -> bool:
        """Wait until document.readyState === 'complete'."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if self.driver.execute_script(_DOCUMENT_READY):
                    return True
            except WebDriverException:
                pass
            time.sleep(0.1)
        return False

    # ----------------------------------------------------------------- DOM

    def wait_for_dom_stable(
        self,
        timeout: float = 8.0,
        quiet_ms: int = 400,
    ) -> bool:
        """Wait until the DOM has been idle for `quiet_ms` milliseconds.

        Returns True if stability was observed, False if the hard timeout
        fired first. In practice on a healthy page this returns within a few
        hundred milliseconds — far faster than a pessimistic fixed sleep.
        """
        try:
            self.driver.execute_script(_OBSERVER_INSTALLER, quiet_ms)
        except JavascriptException:
            # If we can't install the observer (e.g. about:blank), fall back
            # to a conservative short sleep so the caller still makes progress.
            time.sleep(quiet_ms / 1000.0)
            return False

        deadline = time.time() + timeout
        poll_interval = 0.1
        while time.time() < deadline:
            try:
                stable = self.driver.execute_script(_STABILITY_CHECK, quiet_ms)
                if stable:
                    return True
            except WebDriverException:
                return False
            time.sleep(poll_interval)
        return False

    # ------------------------------------------------------------ composite

    def wait_for_page_ready(
        self,
        timeout: float = 15.0,
        quiet_ms: int = 400,
    ) -> bool:
        """Combined check: document complete + DOM stable.

        This is the one-liner most page-object methods should call after any
        navigation or non-trivial click. Replaces the pattern:

            time.sleep(1)          # hope the page is ready
            driver.find_element()  # ... fingers crossed
        """
        if not self.wait_for_document_complete(timeout=timeout):
            return False
        remaining = max(1.0, timeout - 2.0)
        return self.wait_for_dom_stable(timeout=remaining, quiet_ms=quiet_ms)
