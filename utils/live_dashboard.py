"""
LiveDashboard — Real-time WebSocket-driven test execution monitor.

Built by Claude Opus 4.7.

Design goals
------------
* Zero-configuration: drop in, and when the test suite runs, the browser
  opens to a live dashboard. No manual server start, no port config for the
  happy path.
* Thread-safe emit API: behave runs on the main thread; the Flask-SocketIO
  server runs on a daemon thread. The emit methods exposed here are safe to
  call from any thread because SocketIO.emit acquires its own locks.
* Graceful degradation: if Flask / Flask-SocketIO isn't installed or the
  port is occupied, we no-op silently so the test suite still passes.
* Stateful snapshot on connect: late-joining browser tabs get the full
  current run state so they can render correctly mid-run.

Architecture
------------
    behave hook ──► LiveDashboard.emit_*()  ──► socketio.emit(...)
                         (main thread)              (thread-safe)
                                                        │
                                                        ▼
                                                  WebSocket frame
                                                        │
                                                        ▼
                                            browser tab (JS client)

The dashboard runs on 127.0.0.1:<port> (default 5555). If the port is in
use we scan upward for a free one. The chosen URL is printed to stdout
and opened in the default browser on start().
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from typing import Any, Dict, List, Optional


def _safe_print(line: str) -> None:
    """Print line, falling back to ASCII on terminals that can't handle Unicode."""
    try:
        print(line)
    except UnicodeEncodeError:
        try:
            enc = sys.stdout.encoding or "ascii"
            print(line.encode(enc, errors="replace").decode(enc, errors="replace"))
        except Exception:
            print(line.encode("ascii", errors="replace").decode("ascii"))

# All imports are wrapped so a missing dependency simply disables the
# dashboard rather than breaking the test suite.
try:
    from flask import Flask, render_template
    from flask_socketio import SocketIO

    _FLASK_OK = True
except Exception:  # pragma: no cover - import guard
    _FLASK_OK = False


_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_TEMPLATES_DIR = os.path.join(_PROJECT_ROOT, "templates")


def _find_open_port(start: int = 5555, attempts: int = 20) -> Optional[int]:
    """Return the first bindable port at or above `start`, or None."""
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return None


class LiveDashboard:
    """Singleton-style live dashboard. Use the module-level LIVE instance."""

    def __init__(self) -> None:
        self.enabled: bool = False
        self.port: Optional[int] = None
        self.url: Optional[str] = None

        self.app = None
        self.socketio = None
        self._thread: Optional[threading.Thread] = None
        self._started: bool = False

        # Authoritative run state — snapshot sent to any newly-connected tab.
        self.state: Dict[str, Any] = _fresh_state()

    # ================================================================= start

    def start(self, port: int = 5555, auto_open: bool = True) -> None:
        """Spin up the Flask-SocketIO server on a daemon thread."""
        if self._started:
            return
        if not _FLASK_OK:
            print("  [LiveDashboard] flask / flask-socketio not installed — "
                  "dashboard disabled.")
            return
        if os.getenv("CI") or os.getenv("LIVE_DASHBOARD") == "0":
            # CI doesn't need (and can't display) a browser dashboard.
            return

        chosen = _find_open_port(start=port)
        if chosen is None:
            print("  [LiveDashboard] could not find a free port — disabled.")
            return

        self.port = chosen
        self.url = f"http://127.0.0.1:{self.port}/"

        self.app = Flask(
            __name__,
            template_folder=_TEMPLATES_DIR,
            static_folder=_TEMPLATES_DIR,  # reuse for any static files
            static_url_path="/static",
        )
        self.app.config["SECRET_KEY"] = "self-healing-dashboard"

        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode="threading",
            logger=False,
            engineio_logger=False,
        )

        self._register_handlers()

        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

        # Give the server a beat to bind before we open the browser.
        time.sleep(0.4)

        self.enabled = True
        _safe_print("")
        _safe_print("  ┌────────────────────────────────────────────────────────┐")
        _safe_print(f"  │  LIVE DASHBOARD : {self.url:<36}│")
        _safe_print("  │  Browser tab will open automatically.                  │")
        _safe_print("  └────────────────────────────────────────────────────────┘")
        _safe_print("")

        if auto_open:
            try:
                webbrowser.open(self.url)
            except Exception:
                pass

    def _serve(self) -> None:
        # allow_unsafe_werkzeug is required to run the dev server outside
        # the main thread (Flask-SocketIO guardrail). We're local-only and
        # the lifetime of the process is bounded by the test run, so this
        # is safe.
        try:
            self.socketio.run(
                self.app,
                host="127.0.0.1",
                port=self.port,
                allow_unsafe_werkzeug=True,
                debug=False,
                use_reloader=False,
                log_output=False,
            )
        except Exception as e:  # pragma: no cover
            print(f"  [LiveDashboard] server error: {e}")

    def _register_handlers(self) -> None:
        @self.app.route("/")
        def index():
            return render_template("dashboard.html")

        @self.app.route("/healthz")
        def healthz():
            return {"ok": True, "url": self.url}

        @self.socketio.on("connect")
        def on_connect():
            # New client connected — send the current run snapshot so the
            # dashboard renders correctly even if the browser joined late.
            self.socketio.emit("state.snapshot", self.state)

    # ============================================================== emitting

    def _emit(self, event: str, payload: Dict[str, Any]) -> None:
        if not self.enabled or self.socketio is None:
            return
        try:
            self.socketio.emit(event, payload)
        except Exception:
            # Never let a dashboard hiccup fail a test.
            pass

    # ------------------------------------------------------------------ run

    def run_start(self, total_scenarios: int) -> None:
        self.state = _fresh_state()
        self.state["status"] = "running"
        self.state["started_at"] = time.time()
        self.state["total_scenarios"] = total_scenarios
        self._emit("run.start", {
            "total_scenarios": total_scenarios,
            "started_at": self.state["started_at"],
        })

    def run_end(self) -> None:
        self.state["status"] = "completed"
        self.state["ended_at"] = time.time()
        duration = self.state["ended_at"] - (self.state["started_at"] or self.state["ended_at"])
        payload = {
            "status": "completed",
            "duration_s": duration,
            "passed": self.state["passed"],
            "failed": self.state["failed"],
            "healed": self.state["healed"],
            "total_scenarios": self.state["total_scenarios"],
        }
        self._emit("run.end", payload)

    # -------------------------------------------------------------- feature

    def feature_start(self, name: str) -> None:
        self.state["current_feature"] = name
        self._emit("feature.start", {"name": name})

    def feature_end(self, name: str, status: str) -> None:
        self._emit("feature.end", {"name": name, "status": status})

    # ------------------------------------------------------------- scenario

    def scenario_start(self, name: str, tags: List[str], feature: str) -> None:
        self.state["current_scenario"] = name
        self.state["current_scenario_tags"] = tags
        self.state["scenarios_run"] += 0  # no-op; updated at scenario_end
        self._emit("scenario.start", {
            "name": name,
            "feature": feature,
            "tags": tags,
            "started_at": time.time(),
        })

    def scenario_end(self, name: str, status: str, duration_s: float) -> None:
        self.state["scenarios_run"] += 1
        if status == "passed":
            self.state["passed"] += 1
        elif status == "failed":
            self.state["failed"] += 1
        self._emit("scenario.end", {
            "name": name,
            "status": status,
            "duration_s": duration_s,
            "scenarios_run": self.state["scenarios_run"],
            "total_scenarios": self.state["total_scenarios"],
            "passed": self.state["passed"],
            "failed": self.state["failed"],
        })

    # ------------------------------------------------------------------ step

    def step_start(self, keyword: str, name: str) -> None:
        self.state["current_step"] = f"{keyword} {name}".strip()
        self._emit("step.start", {
            "keyword": keyword,
            "name": name,
            "started_at": time.time(),
        })

    def step_end(self, keyword: str, name: str, status: str, duration_s: float) -> None:
        self._emit("step.end", {
            "keyword": keyword,
            "name": name,
            "status": status,
            "duration_s": duration_s,
        })

    # ------------------------------------------------------------------ heal

    def heal(self, event: Dict[str, Any]) -> None:
        self.state["healed"] += 1
        self._emit("heal", event)


def _fresh_state() -> Dict[str, Any]:
    return {
        "status": "idle",
        "started_at": None,
        "ended_at": None,
        "total_scenarios": 0,
        "scenarios_run": 0,
        "passed": 0,
        "failed": 0,
        "healed": 0,
        "current_feature": "",
        "current_scenario": "",
        "current_scenario_tags": [],
        "current_step": "",
    }


LIVE = LiveDashboard()
