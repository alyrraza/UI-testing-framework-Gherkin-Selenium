"""
HealingReport — Generates the self-healing HTML dashboard + suggested fixes.

Built by Claude Opus 4.7.

Produces two artifacts at the end of a test run:

    healing-report/index.html    — animated, self-contained dashboard.
    healing-report/suggested_fixes.md — ready-to-apply locator repairs.

The dashboard is a single HTML file (no external deps, no build step) that
renders healing metrics, a timeline of recoveries, confidence distribution,
and full details for each event. It is designed to look *great* on camera —
dark theme, gradient accents, smooth entrance animations — so recoveries are
unambiguously visible in a demo video.
"""

from __future__ import annotations

import base64
import html
import json
import os
from datetime import datetime
from typing import List

from utils.healing_logger import HEALING_LOGGER, HealingEvent


REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "healing-report")


def generate_all() -> None:
    """Entry point: write the HTML dashboard and the markdown fixes file."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    events = HEALING_LOGGER.events

    html_path = os.path.join(REPORT_DIR, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(_render_html(events))

    fixes_path = os.path.join(REPORT_DIR, "suggested_fixes.md")
    with open(fixes_path, "w", encoding="utf-8") as f:
        f.write(_render_fixes(events))

    print(f"\n  Healing dashboard : {os.path.abspath(html_path)}")
    print(f"  Suggested fixes   : {os.path.abspath(fixes_path)}\n")


# ============================================================ HTML dashboard


def _render_html(events: List[HealingEvent]) -> str:
    total = len(events)
    avg_conf = HEALING_LOGGER.avg_confidence() * 100 if total else 0.0
    stages = HEALING_LOGGER.events_by_stage()
    by_stage = {k: len(v) for k, v in stages.items()}

    cards_html = "".join(_render_event_card(i, e) for i, e in enumerate(events))
    if not events:
        cards_html = (
            "<div class='empty'>"
            "<div class='empty-icon'>✓</div>"
            "<div class='empty-title'>No healing events recorded</div>"
            "<div class='empty-sub'>All locators resolved on first attempt. "
            "To see self-healing in action, intentionally break a locator "
            "in a page object and re-run the tests.</div>"
            "</div>"
        )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stages_json = json.dumps(by_stage)

    return _HTML_TEMPLATE.format(
        total=total,
        avg_conf=f"{avg_conf:.0f}",
        fallback_count=by_stage.get("fallback-strategy", 0),
        similarity_count=by_stage.get("dom-similarity", 0),
        cards=cards_html,
        generated_at=generated_at,
        stages_json=stages_json,
    )


def _render_event_card(idx: int, e: HealingEvent) -> str:
    confidence_pct = int(e.confidence * 100)
    conf_class = (
        "high" if confidence_pct >= 80
        else "mid" if confidence_pct >= 65
        else "low"
    )
    stage_label = {
        "fallback-strategy": "Fallback Strategy",
        "dom-similarity": "DOM Similarity Scan",
    }.get(e.stage, e.stage)

    screenshot_html = ""
    if e.screenshot_png:
        b64 = base64.b64encode(e.screenshot_png).decode("ascii")
        screenshot_html = (
            f"<div class='screenshot'>"
            f"<img src='data:image/png;base64,{b64}' alt='heal screenshot'/>"
            f"</div>"
        )

    scenario_line = ""
    if e.scenario_name:
        scenario_line = (
            f"<div class='scenario'>"
            f"<span class='label'>scenario</span>"
            f"<span>{html.escape(e.scenario_name)}</span>"
            f"</div>"
        )

    return f"""
    <article class='card' style='animation-delay:{idx * 0.08}s'>
        <header class='card-head'>
            <div class='badge heal'>SELF-HEAL</div>
            <h3>{html.escape(e.locator_name)}</h3>
            <div class='conf conf-{conf_class}'>{confidence_pct}%</div>
        </header>
        <div class='stage'>via {stage_label}</div>
        {scenario_line}
        <div class='diff'>
            <div class='diff-row removed'>
                <span class='marker'>−</span>
                <code>{html.escape(e.original_strategy)}</code>
            </div>
            <div class='diff-row added'>
                <span class='marker'>+</span>
                <code>{html.escape(e.healed_strategy)}</code>
            </div>
        </div>
        {f"<div class='desc'>{html.escape(e.description)}</div>" if e.description else ""}
        {screenshot_html}
    </article>
    """


# ============================================================ Suggested fixes


def _render_fixes(events: List[HealingEvent]) -> str:
    if not events:
        return (
            "# Suggested Locator Fixes\n\n"
            "No healing events recorded in this run — nothing to suggest.\n"
        )

    lines = [
        "# Suggested Locator Fixes",
        "",
        "Generated by the self-healing engine. Each entry shows a locator that ",
        "was auto-repaired at runtime and the recommended source-code update.",
        "",
        f"Total events: **{len(events)}**  ",
        f"Avg confidence: **{HEALING_LOGGER.avg_confidence() * 100:.0f}%**",
        "",
        "---",
        "",
    ]

    for e in events:
        lines += [
            f"## `{e.locator_name}`",
            "",
            f"- **Stage**: {e.stage}",
            f"- **Confidence**: {int(e.confidence * 100)}%",
            f"- **Scenario**: {e.scenario_name or '(unknown)'}",
            "",
            "```diff",
            f"- {e.original_strategy}",
            f"+ {e.healed_strategy}",
            "```",
            "",
        ]

    return "\n".join(lines)


# ================================================================= template


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Self-Healing Report · Claude Opus 4.7</title>
<style>
  :root {{
    --bg: #0b0f17;
    --bg-elev: #131a26;
    --bg-card: #1a2332;
    --text: #e7edf5;
    --text-dim: #8a97ab;
    --border: #253142;
    --accent: #00d9a3;
    --accent-glow: rgba(0, 217, 163, 0.35);
    --red: #ff6a7a;
    --amber: #ffb454;
    --blue: #6fa8ff;
    --grad: linear-gradient(135deg, #00d9a3 0%, #6fa8ff 50%, #b48dff 100%);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'SF Mono', 'JetBrains Mono', 'Fira Code', Menlo, monospace;
    -webkit-font-smoothing: antialiased;
    min-height: 100vh;
  }}
  body {{
    background:
      radial-gradient(ellipse at top left, rgba(0, 217, 163, 0.08), transparent 40%),
      radial-gradient(ellipse at top right, rgba(180, 141, 255, 0.08), transparent 40%),
      var(--bg);
  }}
  .wrap {{ max-width: 1200px; margin: 0 auto; padding: 48px 32px 96px; }}

  header.hero {{
    text-align: center;
    padding: 24px 0 56px;
    animation: fadeDown 0.8s ease both;
  }}
  .eyebrow {{
    display: inline-block;
    letter-spacing: 0.2em;
    font-size: 11px;
    color: var(--accent);
    background: rgba(0, 217, 163, 0.08);
    border: 1px solid rgba(0, 217, 163, 0.25);
    padding: 6px 14px;
    border-radius: 999px;
    margin-bottom: 20px;
  }}
  h1 {{
    font-size: 44px;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: var(--grad);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 14px;
  }}
  .subtitle {{
    color: var(--text-dim);
    font-size: 15px;
    max-width: 640px;
    margin: 0 auto;
    line-height: 1.6;
  }}
  .claude-sig {{
    margin-top: 18px;
    font-size: 12px;
    color: var(--text-dim);
    letter-spacing: 0.15em;
  }}
  .claude-sig b {{ color: var(--accent); }}

  .stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 48px;
  }}
  .stat {{
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.6s ease both;
  }}
  .stat:nth-child(1) {{ animation-delay: 0.1s; }}
  .stat:nth-child(2) {{ animation-delay: 0.2s; }}
  .stat:nth-child(3) {{ animation-delay: 0.3s; }}
  .stat:nth-child(4) {{ animation-delay: 0.4s; }}
  .stat::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: var(--grad);
    opacity: 0;
    transition: opacity 0.3s;
  }}
  .stat:hover::before {{ opacity: 0.04; }}
  .stat-label {{
    font-size: 11px;
    letter-spacing: 0.15em;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-bottom: 12px;
  }}
  .stat-value {{
    font-size: 38px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text);
  }}
  .stat-value .unit {{ font-size: 16px; color: var(--text-dim); margin-left: 4px; }}

  section.timeline {{ margin-top: 8px; }}
  section.timeline h2 {{
    font-size: 18px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }}

  .card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 16px;
    animation: slideIn 0.6s ease both;
    transition: border-color 0.2s, transform 0.2s;
  }}
  .card:hover {{
    border-color: var(--accent);
    transform: translateY(-2px);
  }}
  .card-head {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 10px;
  }}
  .badge.heal {{
    background: var(--accent);
    color: #0b0f17;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.15em;
    padding: 4px 10px;
    border-radius: 6px;
    box-shadow: 0 0 20px var(--accent-glow);
  }}
  .card h3 {{
    font-size: 17px;
    flex: 1;
    font-weight: 600;
  }}
  .conf {{
    font-weight: 700;
    font-size: 15px;
    padding: 4px 12px;
    border-radius: 8px;
  }}
  .conf-high {{ color: var(--accent); background: rgba(0, 217, 163, 0.12); }}
  .conf-mid  {{ color: var(--amber);  background: rgba(255, 180, 84, 0.12); }}
  .conf-low  {{ color: var(--red);    background: rgba(255, 106, 122, 0.12); }}
  .stage {{
    color: var(--text-dim);
    font-size: 12px;
    letter-spacing: 0.05em;
    margin-bottom: 14px;
  }}
  .scenario {{
    font-size: 12px;
    margin-bottom: 14px;
    color: var(--text-dim);
  }}
  .scenario .label {{
    color: var(--blue);
    margin-right: 8px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-size: 10px;
  }}
  .diff {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 13px;
  }}
  .diff-row {{ display: flex; align-items: baseline; gap: 10px; padding: 3px 0; }}
  .diff-row .marker {{
    font-weight: 700;
    font-size: 14px;
    width: 14px;
    text-align: center;
  }}
  .diff-row.removed {{ color: var(--red); }}
  .diff-row.removed .marker {{ color: var(--red); }}
  .diff-row.added {{ color: var(--accent); }}
  .diff-row.added .marker {{ color: var(--accent); }}
  .diff-row code {{ font-family: inherit; word-break: break-all; }}
  .desc {{
    margin-top: 12px;
    color: var(--text-dim);
    font-size: 13px;
    line-height: 1.6;
  }}
  .screenshot {{
    margin-top: 14px;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
  }}
  .screenshot img {{ display: block; width: 100%; }}

  .empty {{
    text-align: center;
    padding: 80px 20px;
    background: var(--bg-elev);
    border: 1px dashed var(--border);
    border-radius: 16px;
  }}
  .empty-icon {{
    font-size: 48px;
    color: var(--accent);
    margin-bottom: 16px;
  }}
  .empty-title {{ font-size: 20px; margin-bottom: 8px; }}
  .empty-sub {{ color: var(--text-dim); font-size: 14px; max-width: 520px; margin: 0 auto; line-height: 1.6; }}

  footer.page-foot {{
    text-align: center;
    color: var(--text-dim);
    font-size: 12px;
    margin-top: 64px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
  }}

  @keyframes fadeDown {{
    from {{ opacity: 0; transform: translateY(-20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  @keyframes slideIn {{
    from {{ opacity: 0; transform: translateX(-16px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
  }}

  @media (max-width: 720px) {{
    .stats {{ grid-template-columns: repeat(2, 1fr); }}
    h1 {{ font-size: 32px; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <span class="eyebrow">SELF-HEALING TEST FRAMEWORK</span>
    <h1>Locator Recovery Report</h1>
    <p class="subtitle">
      Every broken locator automatically repaired at runtime by the SmartLocator
      engine — multi-strategy fallback + DOM similarity scoring, no external
      services, no AI calls at test time.
    </p>
    <div class="claude-sig">ENGINEERED BY <b>CLAUDE OPUS 4.7</b></div>
  </header>

  <section class="stats">
    <div class="stat">
      <div class="stat-label">Total Heals</div>
      <div class="stat-value">{total}</div>
    </div>
    <div class="stat">
      <div class="stat-label">Avg Confidence</div>
      <div class="stat-value">{avg_conf}<span class="unit">%</span></div>
    </div>
    <div class="stat">
      <div class="stat-label">Fallback Hits</div>
      <div class="stat-value">{fallback_count}</div>
    </div>
    <div class="stat">
      <div class="stat-label">Similarity Scans</div>
      <div class="stat-value">{similarity_count}</div>
    </div>
  </section>

  <section class="timeline">
    <h2>Healing Timeline</h2>
    {cards}
  </section>

  <footer class="page-foot">
    Generated {generated_at} · Self-healing engine © SmartLocator
  </footer>

</div>
<script>
  // Reserved for future enhancements — kept minimal so the dashboard is
  // a single self-contained file that needs no build step to open.
  window.__healingStages = {stages_json};
</script>
</body>
</html>
"""
