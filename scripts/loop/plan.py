#!/usr/bin/env python3
"""The planner — the deterministic decision the content loop makes each day.

Given the ledger (`_data/loop/runs/`), the config (`_data/loop/config.yml`), the
number of loop pull requests still awaiting review, the activity digest
(scripts/loop/signals.py) and the hub's open editorial directives
(scripts/loop/directives.py), decide — without a model — exactly one of:

  directive  a new article is due and the hub has filed an unclaimed `write`
           directive: the topic is the hub's; the plan carries the brief;
  new      a new article is due: offer the most-overdue section first, the best
           unspent stories, and let the writer choose the angle;
  improve  an improvement is due: offer the pages the inventory says are thin or
           stale, boosted when recent activity touched their subject;
  idle     nothing is due, the review queue is full, or there is no unspent
           activity to write about — recorded with the reason, never silent.

The cadence is self-correcting: whichever of "new" and "improve" is more overdue
runs first, so a skipped day is caught up rather than doubled. Pure where it
matters (`decide()` takes every observation as an argument and is exercised by
the self-test); the CLI does the observing.

Usage:
  python3 scripts/loop/plan.py [--today D] [--open-prs N] [--mode auto|new|improve|directive]
                               [--section S] [--window N] [--no-remote] [--out DIR] [--json]
  python3 scripts/loop/plan.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402
import directives as _directives  # noqa: E402
import ledger  # noqa: E402

INF = float("inf")
DIRECTIVE_KEYS = ("number", "url", "title", "brief", "pillar", "priority", "kind", "path", "key")
DATED_POST_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(?!index\b)")


# --------------------------------------------------------------------------- #
# Observations that live on disk
# --------------------------------------------------------------------------- #

def newest_post_dates(root: Path) -> dict[str, _dt.date | None]:
    """section -> the newest dated post on disk (filename date), ignoring index stubs."""
    out: dict[str, _dt.date | None] = {}
    for sec in _lib.SECTIONS:
        newest = None
        for p in (root / "pages" / "_posts" / sec).glob("*.md"):
            m = DATED_POST_RE.match(p.name)
            d = _lib.parse_date(m.group(1)) if m else None
            if d and (newest is None or d > newest):
                newest = d
        out[sec] = newest
    return out


def count_open_loop_prs(prefix: str = "loop/") -> int | None:
    """Open PRs whose head branch starts with `loop/`, via gh; None when gh can't tell."""
    if not shutil.which("gh"):
        return None
    try:
        res = subprocess.run(["gh", "pr", "list", "--state", "open", "--limit", "100", "--json", "headRefName"],
                             capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if res.returncode != 0:
        return None
    try:
        prs = json.loads(res.stdout)
    except json.JSONDecodeError:
        return None
    return sum(1 for p in prs if str(p.get("headRefName", "")).startswith(prefix))


# --------------------------------------------------------------------------- #
# The pure decision
# --------------------------------------------------------------------------- #

def section_ring(config: dict, runs: list[dict], post_dates: dict, forced: str | None = None) -> list[dict]:
    """The rotation, most-overdue first. `last_served` is the later of the ledger's
    last new piece in that section and the newest dated post on disk."""
    ring = [str(s) for s in ((config.get("sections") or {}).get("ring") or list(_lib.SECTIONS))]
    rows = []
    for idx, sec in enumerate(ring):
        from_ledger = max((_lib.parse_date(r.get("date")) for r in runs
                           if r.get("mode") == "new" and str(r.get("section")) == sec), default=None)
        from_disk = post_dates.get(sec)
        cands = [d for d in (from_ledger, from_disk) if d]
        last = max(cands) if cands else None
        rows.append({"section": sec, "last_served": last.isoformat() if last else None, "_sort": (last or _dt.date.min, idx)})
    rows.sort(key=lambda r: r["_sort"])
    for r in rows:
        r.pop("_sort")
    if forced:
        forced = forced.strip().lower()
        rows.sort(key=lambda r: 0 if r["section"] == forced else 1)
    return rows


def cadence_state(config: dict, runs: list[dict], today: _dt.date) -> dict:
    cad = config.get("cadence") or {}
    new_every = int(cad.get("new_every_days", 2) or 2)
    imp_every = int(cad.get("improve_every_days", 2) or 2)
    last_new = ledger.last_run(runs, "new")
    last_imp = ledger.last_run(runs, "improve")

    def since(rec):
        d = _lib.parse_date(rec.get("date")) if rec else None
        return (today - d).days if d else None

    ds_new, ds_imp = since(last_new), since(last_imp)
    return {
        "new_every_days": new_every, "improve_every_days": imp_every,
        "last_new": {"date": last_new["date"], "id": last_new.get("id", "")} if last_new else None,
        "last_improve": {"date": last_imp["date"], "id": last_imp.get("id", "")} if last_imp else None,
        "days_since_new": ds_new, "days_since_improve": ds_imp,
        "new_due": ds_new is None or ds_new >= new_every,
        "improve_due": ds_imp is None or ds_imp >= imp_every,
        "overdue_new": INF if ds_new is None else ds_new - new_every,
        "overdue_improve": INF if ds_imp is None else ds_imp - imp_every,
    }


def improve_candidates(config: dict, runs: list[dict], rows: list[dict], stories: list[dict],
                       today: _dt.date, stale_days: int = 180) -> list[dict]:
    imp = config.get("improve") or {}
    cooldown = int(imp.get("cooldown_days", 60) or 60)
    exclude = {str(s) for s in (imp.get("exclude_sections") or [])}
    top = int(imp.get("top", 3) or 3)
    related_map = imp.get("related_pages") or {}
    improved = ledger.improved_paths(runs)
    active_areas: list[str] = []
    for s in stories:
        for a in s.get("areas") or []:
            if a not in active_areas:
                active_areas.append(a)
    boost: dict[str, list[str]] = {}
    for area in active_areas:
        for path in related_map.get(area) or []:
            boost.setdefault(str(path), []).append(area)
    out = []
    for r in rows:
        path = str(r.get("path", ""))
        if not path or str(r.get("section", "")) in exclude:
            continue
        last = _lib.parse_date(improved.get(path))
        if last and (today - last).days < cooldown:
            continue
        age = int(r.get("age_days") or 0)
        stale_score = round(min(2.0, age / max(1, stale_days)), 2)
        thin_score = 1.0 if r.get("thin") else 0.0
        related = 2.0 if path in boost else 0.0
        reasons = []
        if stale_score:
            reasons.append(f"{age}d since lastmod")
        if thin_score:
            reasons.append(f"thin ({r.get('words')} words)")
        if related:
            reasons.append("recent activity touched its subject: " + ", ".join(boost[path]))
        out.append({"path": path, "section": r.get("section"), "title": r.get("title", ""), "words": r.get("words"),
                    "age_days": age, "score": round(stale_score + thin_score + related, 2), "reasons": reasons})
    out.sort(key=lambda c: (-c["score"], -c["age_days"], c["path"]))
    return out[:top]


def decide(*, today: _dt.date, config: dict, runs: list[dict], open_prs: int | None, stories_fn,
           inventory_rows: list[dict], post_dates: dict, forced_mode: str | None = None,
           forced_section: str | None = None, repo: str = "", directives: list[dict] | None = None) -> dict:
    """`directives` is the ranked, unclaimed list from directives.gather(); only its
    `write` entries are the planner's (refresh belongs to the review lane)."""
    caps = config.get("caps") or {}
    sig = config.get("signals") or {}
    max_prs = int(caps.get("max_open_prs", 2) or 2)
    window = int(sig.get("window_days", 30) or 30)
    max_window = int(sig.get("max_window_days", 180) or 180)
    top = int(sig.get("top", 6) or 6)
    notes: list[str] = []

    cad = cadence_state(config, runs, today)
    blocked = open_prs is not None and open_prs >= max_prs
    if open_prs is None:
        notes.append("open loop PRs unknown (no gh) — assuming 0; the workflow passes the real count")
    writes = [d for d in (directives or []) if d.get("kind") == "write"]
    directive = writes[0] if writes else None

    def directive_reason(d: dict) -> str:
        return f"editorial directive #{d.get('number')} ({d.get('priority')}) goes ahead of a new article — {d.get('title')}"

    if forced_mode in ("new", "improve"):
        mode, reason, directive = forced_mode, f"forced by the operator ({forced_mode})", None
    elif forced_mode == "directive":
        mode, reason = ("directive", "forced by the operator (directive) — " + directive_reason(directive)) if directive \
            else ("idle", "forced directive, but no unclaimed write directive is open")
    elif blocked:
        mode, reason, directive = "idle", f"{open_prs}/{max_prs} loop PRs already open — backpressure; the human is the bottleneck by design", None
    elif cad["new_due"] and (not cad["improve_due"] or cad["overdue_new"] >= cad["overdue_improve"]):
        if directive:
            # The hub's topic takes the new slot; the cadence is untouched (the run
            # is recorded as mode `new`, with the directive linked).
            mode, reason = "directive", directive_reason(directive)
        else:
            mode = "new"
            reason = ("first run — a new article is due" if cad["days_since_new"] is None
                      else f"{cad['days_since_new']} day(s) since the last new article (every {cad['new_every_days']})")
    elif cad["improve_due"]:
        mode, directive = "improve", None
        reason = ("first improvement — due" if cad["days_since_improve"] is None
                  else f"{cad['days_since_improve']} day(s) since the last improvement (every {cad['improve_every_days']})")
    else:
        mode, directive = "idle", None
        reason = (f"nothing due — next new in {cad['new_every_days'] - cad['days_since_new']} day(s), "
                  f"next improvement in {cad['improve_every_days'] - cad['days_since_improve']} day(s)")
    if mode != "directive":
        directive = None
    if writes and mode in ("new", "improve", "idle") and forced_mode not in ("new", "improve"):
        notes.append(f"{len(writes)} unclaimed write directive(s) waiting (first: #{writes[0].get('number')}) — taken when a new article is next due")

    # Activity: widen the window once when the default window is fully spent.
    result = stories_fn(window)
    live = [s for s in result.get("stories", []) if not s.get("spent") and s.get("score", 0) > 0]
    if not live and max_window > window:
        notes.append(f"no unspent activity in {window} days — widened to {max_window}")
        result = stories_fn(max_window)
        window = max_window
        live = [s for s in result.get("stories", []) if not s.get("spent") and s.get("score", 0) > 0]
    offered = live[:top]

    if mode == "new" and not offered:
        if forced_mode != "new" and cad["improve_due"]:
            mode, reason = "improve", "no unspent activity to write about — improving an existing page instead"
        else:
            mode, reason = "idle", f"no unspent activity in {window} days — nothing honest to write about; try again after the next work lands"

    ring = section_ring(config, runs, post_dates, forced_section)
    candidates = improve_candidates(config, runs, inventory_rows, offered, today) if mode != "idle" else []
    if mode == "improve" and not candidates:
        mode, reason = "idle", "nothing to improve — every candidate page is fresh, or on cooldown"

    compact = [{k: s.get(k) for k in ("id", "kind", "repo", "headline", "score", "date_start", "date_end",
                                       "suggested_sections", "areas", "ai_assisted", "top_paths")}
               | {"pr": (s.get("pr") or {}).get("url", ""), "commits": [c["short"] for c in s.get("commits", [])][:12]}
               for s in offered]
    return {
        "generated_at": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
        "today": today.isoformat(), "repo": repo, "mode": mode, "reason": reason,
        "cadence": {k: (None if v == INF else v) for k, v in cad.items()},
        "backpressure": {"open_prs": open_prs, "max_open_prs": max_prs, "blocked": blocked},
        "section": ring[0]["section"] if mode in ("new", "directive") and ring else None,
        "section_ring": ring, "window_days": window, "stories": compact,
        "improve_candidates": candidates, "notes": notes + list(result.get("notes", [])),
        "directive": {k: directive.get(k) for k in DIRECTIVE_KEYS} if directive else None,
        "_signals": result,
    }


# --------------------------------------------------------------------------- #
# Rendering + outputs
# --------------------------------------------------------------------------- #

def render_plan(plan: dict) -> str:
    cad = plan["cadence"]
    bp = plan["backpressure"]

    def ago(d):
        if not d:
            return "never"
        dd = _lib.parse_date(d)
        return f"{d} ({(_lib.parse_date(plan['today']) - dd).days} days ago)" if dd else str(d)

    out = [f"# Content loop plan — {plan['today']}", "", f"**Decision: {plan['mode'].upper()}** — {plan['reason']}", ""]
    out += ["| | |", "|---|---|",
            f"| Last new article | {ago((cad.get('last_new') or {}).get('date'))} |",
            f"| Last improvement | {ago((cad.get('last_improve') or {}).get('date'))} |",
            f"| Cadence | new every {cad['new_every_days']} days, improve every {cad['improve_every_days']} days |",
            f"| Open loop PRs | {bp['open_prs'] if bp['open_prs'] is not None else '?'} / {bp['max_open_prs']} |",
            f"| Activity window | {plan['window_days']} days |", ""]
    for n in plan.get("notes", []):
        out.append(f"- {n}")
    if plan.get("notes"):
        out.append("")
    d = plan.get("directive")
    if d:
        meta = f"{d.get('priority')}" + (f", pillar `{d['pillar']}`" if d.get("pillar") else "")
        out += ["## Editorial directive (the hub's topic — the pull request closes it)", "",
                f"**#{d['number']} — {d['title']}** ({meta}) — {d['url']}", "", f"> {d.get('brief') or '_no brief_'}", ""]
        if d.get("path"):
            out += [f"Document: `{d['path']}`", ""]
        out += [f"Record the run with `--directive {d['url']}`; the first line of the pull-request body is `Closes #{d['number']}`.", ""]
    out.append("## Section ring (most overdue first)")
    out.append("")
    for i, r in enumerate(plan["section_ring"], 1):
        mark = "**" if plan["mode"] in ("new", "directive") and i == 1 else ""
        out.append(f"{i}. {mark}{r['section']}{mark} — last new piece {ago(r['last_served'])}")
    out.append("")
    out.append("## Stories offered (unspent, best first)")
    out.append("")
    if not plan["stories"]:
        out.append("_None._")
    for i, s in enumerate(plan["stories"], 1):
        out.append(f"{i}. `{s['id']}` (score {s['score']}) — {s['headline']} — suggested: {', '.join(s['suggested_sections'] or [])}"
                   + (f" — [PR]({s['pr']})" if s.get("pr") else ""))
    out.append("")
    out.append("Full detail for each story is in `digest.md` (commits, files, changelog, session intent, how to dig in).")
    out.append("")
    out.append("## Improve candidates (best first)")
    out.append("")
    if not plan["improve_candidates"]:
        out.append("_None offered in this mode._")
    for i, c in enumerate(plan["improve_candidates"], 1):
        out.append(f"{i}. `{c['path']}` (score {c['score']}) — {c['title'] or c['section']} — {c['words']} words — {'; '.join(c['reasons']) or 'baseline'}")
    out.append("")
    return "\n".join(out)


def write_outputs(plan: dict, out_dir: Path) -> None:
    import signals as _signals
    out_dir.mkdir(parents=True, exist_ok=True)
    sig = plan.pop("_signals", None)
    (out_dir / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "plan.md").write_text(render_plan(plan) + "\n", encoding="utf-8")
    if sig:
        (out_dir / "signals.json").write_text(json.dumps(sig, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "digest.md").write_text(_signals.render_markdown(sig, len(plan["stories"]) or 6) + "\n", encoding="utf-8")
    gho = os.environ.get("GITHUB_OUTPUT")
    if gho:
        with open(gho, "a", encoding="utf-8") as fh:
            fh.write(f"mode={plan['mode']}\n")
            fh.write(f"section={plan['section'] or ''}\n")
            fh.write(f"reason={_lib.one_line(plan['reason'], 200)}\n")
            fh.write(f"stories={len(plan['stories'])}\n")
            d = plan.get("directive") or {}
            fh.write(f"directive_number={d.get('number') or ''}\n")
            fh.write(f"directive_url={d.get('url') or ''}\n")


# --------------------------------------------------------------------------- #
# Self-test (pure decision, stubbed observations)
# --------------------------------------------------------------------------- #

def self_test() -> int:
    failures: list[str] = []

    def check(name, got, want):
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    cfg = {"cadence": {"new_every_days": 2, "improve_every_days": 2}, "caps": {"max_open_prs": 2},
           "sections": {"ring": ["tech", "corp", "erp", "muses"]},
           "signals": {"window_days": 30, "max_window_days": 180, "top": 3},
           "improve": {"cooldown_days": 60, "exclude_sections": ["case-studies"], "top": 3,
                       "related_pages": {"claude": ["ai-operations.md"], "ci": ["pages/_toolkit/ai-native-practice.md"]}}}
    D = _dt.date
    story = {"id": "session:S1", "kind": "session", "repo": "x/y", "headline": "built the loop", "score": 70.0,
             "date_start": "2026-09-03", "date_end": "2026-09-03", "suggested_sections": ["tech"], "areas": ["claude", "scripts"],
             "ai_assisted": True, "top_paths": [], "pr": None, "commits": [{"short": "abc1234"}], "spent": False}
    spent_story = dict(story, id="pr:1", spent=True, score=0.0)
    calls: list[int] = []

    def stories_ok(window):
        calls.append(window)
        return {"stories": [story, spent_story], "notes": ["home: 2 commit(s)"]}

    def stories_none(window):
        calls.append(window)
        return {"stories": [spent_story], "notes": []}

    rows = [
        {"path": "ai-operations.md", "section": "root", "title": "How an AI-augmented practice runs", "words": 1500, "age_days": 60, "thin": False, "stale": False},
        {"path": "pages/_toolkit/ai-native-practice.md", "section": "toolkit", "title": "AI-native", "words": 2000, "age_days": 200, "thin": False, "stale": True},
        {"path": "pages/_case-studies/x.md", "section": "case-studies", "title": "cs", "words": 300, "age_days": 400, "thin": True, "stale": True},
        {"path": "pages/_services/cloud.md", "section": "services", "title": "Cloud", "words": 650, "age_days": 10, "thin": True, "stale": False},
        {"path": "pages/_posts/tech/old.md", "section": "posts/tech", "title": "Old", "words": 900, "age_days": 300, "thin": False, "stale": True},
    ]
    posts = {"tech": D(2026, 7, 6), "corp": D(2026, 7, 8), "erp": D(2026, 7, 6), "muses": D(2026, 8, 19)}
    base = dict(config=cfg, open_prs=0, stories_fn=stories_ok, inventory_rows=rows, post_dates=posts, repo="x/y")

    # Day 0: nothing recorded -> new, most-overdue section first (tech ties erp; ring order wins).
    p0 = decide(today=D(2026, 9, 5), runs=[], **base)
    check("day0 mode", p0["mode"], "new")
    check("day0 section", p0["section"], "tech")
    check("ring order", [r["section"] for r in p0["section_ring"]], ["tech", "erp", "corp", "muses"])
    check("stories offered", [s["id"] for s in p0["stories"]], ["session:S1"])
    check("candidates in new mode too", p0["improve_candidates"][0]["path"], "ai-operations.md")
    check("case study excluded", any(c["path"].startswith("pages/_case-studies") for c in p0["improve_candidates"]), False)
    check("related boost reason", "claude" in p0["improve_candidates"][0]["reasons"][-1], True)

    runs = [{"id": "r1", "date": "2026-09-05", "mode": "new", "section": "tech", "path": "pages/_posts/tech/2026-09-05-x.md", "signals": ["session:S1"]}]
    p1 = decide(today=D(2026, 9, 6), runs=runs, **base)
    check("day1 improve", p1["mode"], "improve")
    check("day1 no section", p1["section"], None)
    p2 = decide(today=D(2026, 9, 7), runs=runs + [{"id": "r2", "date": "2026-09-06", "mode": "improve", "section": "toolkit", "path": "pages/_toolkit/ai-native-practice.md"}], **base)
    check("day2 new", p2["mode"], "new")
    check("day2 rotation moved on", p2["section"], "erp")
    check("cooldown hides improved page", any(c["path"] == "pages/_toolkit/ai-native-practice.md" for c in p2["improve_candidates"]), False)
    p3 = decide(today=D(2026, 9, 8), runs=runs + [{"id": "r2", "date": "2026-09-06", "mode": "improve", "section": "toolkit", "path": "pages/_toolkit/ai-native-practice.md"},
                                                    {"id": "r3", "date": "2026-09-07", "mode": "new", "section": "erp", "path": "pages/_posts/tech/2026-09-05-x.md"}], **base)
    check("day3 improve", p3["mode"], "improve")
    same_day = decide(today=D(2026, 9, 6), runs=runs + [{"id": "r2", "date": "2026-09-06", "mode": "improve", "section": "toolkit", "path": "p"}], **base)
    check("nothing due -> idle", same_day["mode"], "idle")
    check("idle reason", "nothing due" in same_day["reason"], True)
    # A missed day: new is more overdue than improve -> new first.
    missed = decide(today=D(2026, 9, 9), runs=[{"id": "a", "date": "2026-09-05", "mode": "new", "section": "tech", "path": "p"},
                                                 {"id": "b", "date": "2026-09-08", "mode": "improve", "section": "toolkit", "path": "p"}], **base)
    check("catch-up prefers most overdue", missed["mode"], "new")
    # Backpressure.
    blocked = decide(today=D(2026, 9, 5), runs=[], **dict(base, open_prs=2))
    check("backpressure idle", blocked["mode"], "idle")
    check("backpressure flag", blocked["backpressure"]["blocked"], True)
    forced = decide(today=D(2026, 9, 5), runs=[], forced_mode="improve", forced_section="muses", **base)
    check("forced mode", forced["mode"], "improve")
    check("forced section first", forced["section_ring"][0]["section"], "muses")
    # No activity: widen once, then fall back to improve (due) or idle.
    calls.clear()
    none_new = decide(today=D(2026, 9, 5), runs=[], **dict(base, stories_fn=stories_none))
    check("widened window", calls, [30, 180])
    check("no activity -> improve", none_new["mode"], "improve")
    check("widen note", any("widened" in n for n in none_new["notes"]), True)
    none_idle = decide(today=D(2026, 9, 5), runs=[{"id": "b", "date": "2026-09-05", "mode": "improve", "section": "t", "path": "p"}],
                       **dict(base, stories_fn=stories_none))
    check("no activity, improve not due -> idle", none_idle["mode"], "idle")
    md = render_plan({k: v for k, v in p0.items() if k != "_signals"})
    check("plan markdown", md.startswith("# Content loop plan — 2026-09-05\n\n**Decision: NEW**"), True)
    check("plan markdown ring", "1. **tech** — last new piece 2026-07-06" in md, True)
    check("no directive -> none carried", p0["directive"], None)
    check("no directive -> no section in plan.md", "## Editorial directive" in md, False)

    # An open, unclaimed `write` directive from the hub takes the new slot.
    directive = {"number": 70, "url": "https://github.com/x/y/issues/70", "title": "Making progress: the essay",
                 "brief": "Write the essay the owner asked for.", "pillar": "ai-operations", "priority": "P1",
                 "kind": "write", "path": None, "key": "making-progress", "slug": "making-progress-the-essay",
                 "site": "bash-365.com", "narrative": "n", "created_at": "2026-10-10T00:00:00Z"}
    with_d = dict(base, directives=[directive])
    pd = decide(today=D(2026, 9, 5), runs=[], **with_d)
    check("directive goes ahead of new", pd["mode"], "directive")
    check("directive carried", pd["directive"], {k: directive[k] for k in DIRECTIVE_KEYS})
    check("directive reason names it", "#70" in pd["reason"] and "P1" in pd["reason"], True)
    check("directive keeps the ring's section", pd["section"], "tech")
    check("directive still offers stories", [s["id"] for s in pd["stories"]], ["session:S1"])
    check("directive needs no activity", decide(today=D(2026, 9, 5), runs=[], **dict(with_d, stories_fn=stories_none))["mode"], "directive")
    waits = decide(today=D(2026, 9, 6), runs=runs, **with_d)
    check("directive waits on an improve day", waits["mode"], "improve")
    check("waiting directive not carried", waits["directive"], None)
    check("waiting directive noted", any("waiting" in n and "#70" in n for n in waits["notes"]), True)
    check("forced new ignores the directive", decide(today=D(2026, 9, 5), runs=[], forced_mode="new", **with_d)["mode"], "new")
    check("forced improve ignores the directive", decide(today=D(2026, 9, 5), runs=[], forced_mode="improve", **with_d)["mode"], "improve")
    check("backpressure beats the directive", decide(today=D(2026, 9, 5), runs=[], **dict(with_d, open_prs=2))["mode"], "idle")
    check("refresh is the review lane's, not the planner's", decide(today=D(2026, 9, 5), runs=[], **dict(base, directives=[dict(directive, kind="refresh")]))["mode"], "new")
    forced_d = decide(today=D(2026, 9, 6), runs=runs, forced_mode="directive", **with_d)
    check("forced directive on an improve day", forced_d["mode"], "directive")
    check("forced directive carried", forced_d["directive"]["number"], 70)
    check("forced directive, none open -> idle", decide(today=D(2026, 9, 5), runs=[], forced_mode="directive", **base)["mode"], "idle")
    mdd = render_plan({k: v for k, v in pd.items() if k != "_signals"})
    check("plan markdown directive decision", mdd.startswith("# Content loop plan — 2026-09-05\n\n**Decision: DIRECTIVE**"), True)
    check("plan markdown directive block", "## Editorial directive" in mdd and "**#70 — Making progress: the essay** (P1, pillar `ai-operations`)" in mdd, True)
    check("plan markdown closes line", "`Closes #70`" in mdd, True)
    check("plan markdown ring mark in directive mode", "1. **tech** — last new piece 2026-07-06" in mdd, True)

    if failures:
        print("plan --self-test: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("plan --self-test: PASS (cadence alternation + catch-up, rotation, backpressure, forcing, widening, candidates, directive ahead of new / none)")
    return 0


# --------------------------------------------------------------------------- #
# CLI — observe, then decide
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description="Decide what the content loop does today.")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today UTC, or LOOP_TODAY)")
    ap.add_argument("--open-prs", type=int, help="open loop PRs (default: ask gh; unknown -> 0)")
    ap.add_argument("--mode", choices=["auto", "new", "improve", "directive"], default="auto",
                    help="force a mode (cadence bypassed, cap not); directive = the hub's first unclaimed write directive")
    ap.add_argument("--section", help="put this section first in the ring")
    ap.add_argument("--window", type=int, help="activity window in days (default: config)")
    ap.add_argument("--no-remote", action="store_true", help="no network: don't read sister repositories or the editorial-directive issues")
    ap.add_argument("--out", help="write plan.json, plan.md, signals.json, digest.md here (e.g. .loop)")
    ap.add_argument("--json", action="store_true", help="print plan.json to stdout")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    import signals as _signals
    sys.path.insert(0, str(_lib.ROOT / "scripts"))
    import content_inventory as _inv  # noqa: E402

    config = _lib.read_yaml(_lib.CONFIG_PATH, default={}) or {}
    if args.window:
        config.setdefault("signals", {})["window_days"] = args.window
    sources = ((_lib.read_yaml(_lib.SOURCES_PATH, default={}) or {}).get("repos")) or []
    today = _lib.parse_date(args.today) if args.today else _lib.today()
    if today is None:
        ap.error(f"bad --today {args.today!r}")
    if args.section and args.section not in _lib.SECTIONS:
        ap.error(f"--section must be one of {_lib.SECTIONS}")
    runs = ledger.load_runs()
    open_prs = args.open_prs if args.open_prs is not None else count_open_loop_prs()
    found = {"directives": [], "notes": ["directives not read (--no-remote)"]} if args.no_remote else _directives.gather(config, runs)

    def stories_fn(window: int) -> dict:
        return _signals.gather(today, window, config, sources, runs, remote=not args.no_remote)

    plan = decide(today=today, config=config, runs=runs, open_prs=open_prs, stories_fn=stories_fn,
                  inventory_rows=_inv.inventory(today), post_dates=newest_post_dates(_lib.ROOT),
                  forced_mode=None if args.mode == "auto" else args.mode, forced_section=args.section,
                  repo=_lib.repo_slug(), directives=found["directives"])
    plan["notes"] = list(found.get("notes", [])) + plan["notes"]
    if args.out:
        write_outputs(plan, Path(args.out))
        print(f"plan: {plan['mode'].upper()} — {plan['reason']}")
        print(f"      section={plan['section'] or '-'} stories={len(plan['stories'])} candidates={len(plan['improve_candidates'])} → {args.out}/plan.md")
        return 0
    plan.pop("_signals", None)
    print(json.dumps(plan, indent=2, ensure_ascii=False) if args.json else render_plan(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
