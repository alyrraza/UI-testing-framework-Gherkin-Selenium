# UI Testing Framework — Self-Healing Edition

A Selenium + Behave (Gherkin BDD) UI-testing framework for the SauceDemo
e-commerce site, **dramatically upgraded by Claude Opus 4.7** with three
production-grade capabilities that most teams never have the time to build:

1. A **three-stage self-healing locator engine** — tests no longer break
   when developers rename IDs or restructure the DOM.
2. A **MutationObserver-based intelligent wait system** — replaces every
   brittle `time.sleep()` call with DOM-stability detection.
3. A **real-time WebSocket execution dashboard** — opens a browser tab the
   moment tests start and streams every feature / scenario / step / heal
   event live.

Plus a self-contained animated post-run **healing report** and a generated
**suggested-fixes markdown** file that tells you exactly which locators to
repair permanently in your source code.

---

## Table of contents

1. [Project origin and what changed](#project-origin-and-what-changed)
2. [High-level architecture](#high-level-architecture)
3. [File-by-file breakdown](#file-by-file-breakdown)
4. [How the pieces connect — workflow walkthrough](#how-the-pieces-connect--workflow-walkthrough)
5. [Running the project](#running-the-project)
6. [How to record the portfolio video](#how-to-record-the-portfolio-video)
7. [LinkedIn caption templates](#linkedin-caption-templates)
8. [Credits](#credits)

---

## Project origin and what changed

### Before Claude

The original project was a solid learning framework by the author:

- Page Object Model pattern (`pages/*.py`)
- Gherkin feature files (`features/*.feature`)
- Data loaders for SQLite, Excel, and Redis (`data/*.py`, `utils/db_utils.py`)
- Allure reporting via `allure-behave`
- GitHub Actions CI pipeline
- Locators were plain `(By, value)` tuples — brittle, no recovery

### After Claude Opus 4.7

Everything above is **preserved unchanged**. Claude's work is **additive
and backwards-compatible** — old tuple locators still work next to the new
system.

New capabilities added:

| Capability                   | New file(s)                                     |
| :--------------------------- | :---------------------------------------------- |
| Self-healing locator engine  | `utils/smart_locator.py`                      |
| Healing event logger         | `utils/healing_logger.py`                     |
| Post-run HTML + MD report    | `utils/healing_report.py`                     |
| MutationObserver smart wait  | `utils/smart_wait.py`                         |
| Live WebSocket dashboard     | `utils/live_dashboard.py`                     |
| Live dashboard UI            | `templates/dashboard.html`                    |
| Behave lifecycle integration | updated `features/environment.py`             |
| Page objects migrated        | updated `pages/base_page.py` + all page files |

---

## High-level architecture

```
                    ┌─────────────────────────────────────────┐
                    │  run_tests.py  (entry point)            │
                    └──────────────────┬──────────────────────┘
                                       │ spawns `behave`
                                       ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │                    features/environment.py                         │
  │   before_all · before_feature · before_scenario · before_step      │
  │   after_step · after_scenario · after_feature · after_all          │
  └─────────────┬─────────────────┬──────────────────┬─────────────────┘
                │                 │                  │
                ▼                 ▼                  ▼
     ┌─────────────────┐  ┌────────────────┐  ┌──────────────────────┐
     │ HEALING_LOGGER  │  │   LIVE (server) │  │ driver_factory       │
     │ (singleton)     │  │ Flask-SocketIO  │  │ Chrome / Firefox     │
     └──────┬──────────┘  └───────┬─────────┘  └──────┬───────────────┘
            │                     │                    │
            │ heal events         │ WebSocket          │ WebDriver
            │                     │                    │
            ▼                     ▼                    ▼
   ┌────────────────────┐  ┌──────────────────┐  ┌───────────────────┐
   │ healing_report.py  │  │ dashboard.html   │  │ pages/*.py        │
   │ writes:            │  │ (browser tab)    │  │ SmartLocators     │
   │  index.html        │  │ live stats,      │  │       │           │
   │  suggested_fixes   │  │ step feed,       │  │       ▼           │
   └────────────────────┘  │ heal feed,       │  │ smart_locator.py  │
                           │ completion       │  │ heals on break,   │
                           │ overlay          │  │ logs to HEALING   │
                           └──────────────────┘  └───────────────────┘
```

---

## File-by-file breakdown

### Core self-healing engine

#### [`utils/smart_locator.py`](utils/smart_locator.py)

The heart of the system. Defines the `SmartLocator` dataclass and its
three-stage healing pipeline.

**Responsibilities**

- Holds an **ordered list of locator strategies** per element plus
  healing hints (`expected_tag`, `expected_text`, `description`).
- `.find(driver)` — tries each strategy in order; if all fail, runs a
  **DOM similarity scan** and scores every candidate on tag/text/attribute
  overlap; accepts the best match above the confidence threshold.
- Emits a `HealingEvent` to `HEALING_LOGGER` the moment anything
  non-trivial happens (fallback or similarity heal).

**Depends on**: `selenium`, `utils/healing_logger`
**Used by**: every page object in `pages/`, `pages/base_page.py`

---

#### [`utils/healing_logger.py`](utils/healing_logger.py)

Singleton event recorder. Broadcasts every heal in three directions at
once: colored console banner, Allure attachment, and live WebSocket frame.

**Responsibilities**

- `HEALING_LOGGER.record(event)` → console print + Allure attach + live emit.
- `HEALING_LOGGER.bind_scenario(...)` called from `environment.py` so
  each heal is tagged with its feature/scenario.
- Aggregates all events in memory for `healing_report.py` to consume.

**Depends on**: `allure` (optional, graceful), `utils/live_dashboard` (optional, graceful)
**Used by**: `utils/smart_locator.py`, `features/environment.py`, `utils/healing_report.py`

---

#### [`utils/healing_report.py`](utils/healing_report.py)

Produces the **post-run healing artifacts** once the suite finishes.

**Responsibilities**

- `generate_all()` → writes
  `healing-report/index.html` (animated dark-theme dashboard) and
  `healing-report/suggested_fixes.md` (ready-to-paste code fix diff).
- Dashboard is a **single self-contained HTML file** — no build step, no
  external deps; embeds screenshots as base64.

**Depends on**: `utils/healing_logger`
**Used by**: `features/environment.py` (`after_all`)

---

#### [`utils/smart_wait.py`](utils/smart_wait.py)

Replaces flaky `time.sleep()` calls across the framework with actual
**DOM-stability detection**.

**Responsibilities**

- Injects a `MutationObserver` into the page via `driver.execute_script`.
- Polls a single boolean flag — “has the DOM been quiet for 400 ms?”
- `wait_for_page_ready()` one-liner combines `document.readyState === 'complete'`
  + `wait_for_dom_stable()` — used by `BasePage.open()`.

**Depends on**: `selenium`
**Used by**: `pages/base_page.py`, all page objects on state-change operations

---

### Real-time live dashboard

#### [`utils/live_dashboard.py`](utils/live_dashboard.py)

Flask-SocketIO server that runs on a daemon thread alongside the test
process. Exposes a thread-safe emit API the behave hooks call into.

**Responsibilities**

- `.start()` on `before_all`: finds a free port (5555+), opens the browser
  tab, binds Flask routes, starts the Socket.IO background loop.
- Keeps an authoritative `state` dict — late-joining browser tabs receive
  a full `state.snapshot` on connect so they render correctly mid-run.
- Silently no-ops in CI (`CI=true`) or when Flask isn't installed.

**Events emitted (WebSocket)**

```
run.start    {total_scenarios, started_at}
feature.start / feature.end
scenario.start / scenario.end
step.start   / step.end
heal         {locator_name, original, healed, confidence, stage, ...}
run.end      {passed, failed, healed, duration_s}
state.snapshot  (on new connection)
```

**Depends on**: `flask`, `flask-socketio`
**Used by**: `features/environment.py`, `utils/healing_logger.py`

---

#### [`templates/dashboard.html`](templates/dashboard.html)

Single-file live dashboard served at `http://127.0.0.1:5555/`.

**UI features**

- Gradient logo mark + connection pill with pulsing dot
- Live elapsed timer
- Hero card: current Feature / Scenario / Step with tag pills + running
  spinner on the step
- 180 px circular progress ring that fills with a gradient stroke
- Four animated counters (Scenarios Run / Passed / Failed / Self-Heals)
  — bump animation on change
- Dual-column feeds: Step Timeline (last 60 steps, pass/fail icon +
  duration) and Self-Heal Events (red → green diff cards with
  confidence chips)
- Completion overlay on `run.end` (passed or failed variant)
- Floating ambient orb background

**Depends on**: `socket.io` (CDN), nothing else

---

### Page objects (all migrated to `SmartLocator`)

All four page files now declare every element as a `SmartLocator` with
3–4 prioritized fallback strategies plus healing hints. Existing methods
(`login()`, `click_checkout()`, etc.) are unchanged from the caller's
perspective.

| File                                                | What changed                                                                                                                     |
| :-------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| [`pages/base_page.py`](pages/base_page.py)           | `click`, `type`, `get_text`, `is_visible` now accept `SmartLocator` or a tuple. Uses `SmartWait` for page readiness. |
| [`pages/login_page.py`](pages/login_page.py)         | 4 elements migrated: username, password, login button, error message                                                             |
| [`pages/inventory_page.py`](pages/inventory_page.py) | 6 elements migrated: title, cart badge / icon, burger menu, logout link                                                          |
| [`pages/cart_page.py`](pages/cart_page.py)           | 4 elements migrated: cart items, checkout / continue buttons, item name                                                          |
| [`pages/checkout_page.py`](pages/checkout_page.py)   | 8 elements migrated across step 1, summary, complete pages                                                                       |

---

### Lifecycle wiring

#### [`features/environment.py`](features/environment.py)

The glue that ties every subsystem into the behave lifecycle.

| Hook                | Actions                                                                                                               |
| :------------------ | :-------------------------------------------------------------------------------------------------------------------- |
| `before_all`      | Reset `HEALING_LOGGER`, start live dashboard, open browser tab, emit `run.start`, print banner                    |
| `before_feature`  | `LIVE.feature_start(name)`                                                                                          |
| `before_scenario` | Spin up WebDriver, tag heal events with scenario name, emit `scenario.start`                                        |
| `before_step`     | Record start time, emit `step.start`                                                                                |
| `after_step`      | Compute duration, emit `step.end` with `passed` / `failed` / duration                                           |
| `after_scenario`  | Attach screenshot on failure, quit WebDriver, emit `scenario.end`                                                   |
| `after_feature`   | Emit `feature.end`                                                                                                  |
| `after_all`       | Print heal summary, generate `healing-report/`, emit `run.end`, linger 2s so the browser receives the final frame |

---

## How the pieces connect — workflow walkthrough

A complete trace of what happens when you run `python run_tests.py`:

### 1. Process boot (`run_tests.py`)

```
python run_tests.py
 └─> subprocess.run(["behave", "--format", "allure_behave.formatter:AllureFormatter", ...])
      └─> behave loads features/environment.py
```

### 2. `before_all` fires

```
environment.before_all(context)
 ├─> HEALING_LOGGER.reset()                 # clear previous events
 ├─> LIVE.start()                            # Flask-SocketIO on 127.0.0.1:5555
 │    ├─> _find_open_port(5555)              # scan for free port
 │    ├─> threading.Thread(target=socketio.run, daemon=True).start()
 │    ├─> time.sleep(0.4)                    # let the server bind
 │    └─> webbrowser.open(url)                # browser tab opens ← USER SEES THIS
 ├─> total = _count_scenarios(context)       # inspect runner for planned count
 ├─> LIVE.run_start(total)                   # emits 'run.start' to any listener
 └─> print banner
```

At this moment:

- The terminal shows the `SELF-HEALING TEST FRAMEWORK` banner.
- A browser tab opens showing the empty Live Dashboard with a
  "CONNECTING…" pill that switches to "LIVE" within ~200 ms.

### 3. First feature: `login.feature`

```
before_feature(context, feature)
 └─> LIVE.feature_start("User Authentication on SauceDemo")
      └─> socketio.emit('feature.start', {name: ...})
           └─> dashboard.html updates #curFeature
```

### 4. First scenario: `Successful login with valid credentials`

```
before_scenario(context, scenario)
 ├─> context.driver = get_driver("chrome")              # Chrome launches
 ├─> HEALING_LOGGER.bind_scenario(feature, scenario)    # tag future heals
 └─> LIVE.scenario_start(name, tags, feature)
      └─> dashboard shows scenario name + tag pills
```

### 5. First step: `Given I am on the SauceDemo login page`

```
before_step(context, step)
 └─> LIVE.step_start("Given", "I am on the SauceDemo login page")
      └─> dashboard spinner appears, current-step text updates

features/steps/login_steps.py:
 └─> step_open_login(context)
      └─> LoginPage(context.driver).open_login()
           └─> BasePage.open("/")
                ├─> driver.get(BASE_URL + "/")
                └─> self.smart_wait.wait_for_page_ready()
                     ├─> wait_for_document_complete()
                     └─> wait_for_dom_stable(quiet_ms=400)
                          └─> injects MutationObserver via execute_script
                          └─> polls until DOM is quiet for 400ms

after_step fires:
 └─> LIVE.step_end("Given", ..., status="passed", duration_s=0.82)
      └─> dashboard adds a ✓ row to Step Timeline with 820ms badge
```

### 6. A locator break triggers self-healing

Suppose the login button's primary ID doesn't exist (simulated by breaking
the first strategy in `pages/login_page.py`):

```
step: "When I click the login button"
 └─> LoginPage.click_login()
      └─> BasePage.click(LOGIN_BUTTON)
           └─> LOGIN_BUTTON.find_clickable(driver)
                └─> SmartLocator.find(driver)
                     ├─> try (By.ID, "button-renamed-by-dev")       ✗ fails
                     ├─> try (By.CSS, "[data-test='login-button']") ✓ succeeds
                     └─> _record_heal(stage="fallback-strategy", confidence=0.9)
                          └─> HealingEvent created
                               ├─> HEALING_LOGGER.record(event)
                               │    ├─> _emit_console → colorized box banner
                               │    ├─> _emit_allure  → attach to Allure step
                               │    └─> _emit_live    → LIVE.heal(event)
                               │         └─> socketio.emit('heal', ...)
                               │              └─> dashboard inserts a
                               │                  purple diff card in the
                               │                  Self-Heal Events feed
                               └─> (event is also stored in HEALING_LOGGER.events)
```

All this happens mid-step, and the test **still passes**.

### 7. Scenario ends

```
after_scenario(context, scenario)
 ├─> if failed: attach_screenshot()                     # Allure
 ├─> context.driver.quit()                              # close Chrome
 └─> LIVE.scenario_end(name, status, duration_s)
      ├─> state.passed += 1 (or failed)
      └─> socketio.emit('scenario.end', {...})
           └─> dashboard bumps "Passed" counter,
               advances progress ring
```

### 8. `after_all` — the finale

```
after_all(context)
 ├─> print heal summary ("3 locator(s) auto-repaired, avg confidence 88%")
 ├─> generate_healing_report()
 │    ├─> write healing-report/index.html
 │    │    └─> renders every event as an animated card with
 │    │        diff, confidence badge, screenshot
 │    └─> write healing-report/suggested_fixes.md
 │         └─> unified-diff per healed locator — paste into page objects
 ├─> LIVE.run_end()
 │    └─> socketio.emit('run.end', {passed, failed, healed, duration_s})
 │         └─> dashboard shows completion overlay (green check or red !)
 └─> sleep(2.0) so the browser receives run.end before the process exits
```

### 9. User closes the browser tab when ready

The healing dashboard (`healing-report/index.html`) remains on disk
and can be opened anytime after the fact:

```
start healing-report/index.html      (Windows)
open  healing-report/index.html      (macOS)
```

---

## Running the project

```bash
# 1. install
pip install -r requirements.txt

# 2. seed local test data (SQLite + Excel)
python data/seed_data.py

# 3. run the suite — this opens the live dashboard in your browser
python run_tests.py

# 4. after the run, open the post-run healing dashboard
start healing-report/index.html      # Windows
open  healing-report/index.html      # macOS

# 5. (optional) Allure report
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### Controlling the live dashboard

- `LIVE_DASHBOARD=0 python run_tests.py` — disables the live dashboard
- In CI (`CI=true`) the live dashboard auto-disables
- Port 5555 busy? The server scans 5555–5574 for a free port automatically

### Triggering self-healing on purpose (for the demo)

Open `pages/login_page.py` and change the first strategy in
`LOGIN_BUTTON.strategies` to something that doesn't exist:

```python
LOGIN_BUTTON = SmartLocator(
    name="login_submit_button",
    ...
    strategies=[
        (By.ID, "button-renamed-by-dev"),             # ← broken on purpose
        (By.CSS_SELECTOR, "[data-test='login-button']"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.XPATH, "//input[@value='Login']"),
    ],
)
```

Re-run `python run_tests.py`. Watch the SELF-HEAL banner in the
terminal and the purple heal card appear in the live dashboard.

## Credits

- **Original framework, Gherkin authoring, Page Object structure, data
  loaders, Allure integration, CI pipeline**: project author.
- **Self-healing engine, intelligent wait system, live WebSocket
  dashboard, post-run healing report, suggested-fixes generator, Allure
  healing attachments, lifecycle wiring, and this README**: **Claude
  Opus 4.7**.
