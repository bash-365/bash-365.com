#!/usr/bin/env python3
"""The content loop's ledger — one YAML record per run under `_data/loop/runs/`.

The ledger is the loop's memory. The planner reads it to know when the last new
article and the last improvement happened (cadence), which section has gone
longest without a piece (rotation), and which pages were improved recently
(cooldown); the miner reads it to know which stories are already spent, so the
same commit is never written up twice; the directive reader (directives.py) reads
it to know which of the hub's editorial directives a run already served, so a
directive whose pull request never said `Closes #n` still counts as spent.

One file per run, never a shared list: two loop pull requests in flight append
two different files and merge without conflict.

Usage:
  python3 scripts/loop/ledger.py --list [--json]
  python3 scripts/loop/ledger.py --last new|improve
  python3 scripts/loop/ledger.py --record --mode new --section tech \\
      --path pages/_posts/tech/2026-09-07-slug.md --title "…" \\
      --signals session:abc,pr:38 --summary "…" [--pr URL] [--date YYYY-MM-DD] \\
      [--directive https://github.com/<owner>/<repo>/issues/N]
  python3 scripts/loop/ledger.py --set-pr <run-id> <pull-request-url>
  python3 scripts/loop/ledger.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402

MODES = ("new", "improve")
ISSUE_URL_RE = re.compile(r"^https://github\.com/[^/\s]+/[^/\s]+/issues/\d+$")

RECORD_HEADER = """\
# Content-loop run record — written by scripts/loop/ledger.py, committed in the
# same pull request as the content it describes. Do not edit by hand except to
# correct a mistake; never delete (the ledger is the loop's memory)."""


def load_runs(runs_dir: Path = _lib.RUNS_DIR) -> list[dict]:
    """Every run record, oldest first (by date, then id). Unreadable files are
    reported on stderr and skipped — one bad record must not stop the loop."""
    runs: list[dict] = []
    if not runs_dir.exists():
        return runs
    for path in sorted(runs_dir.glob("*.yml")):
        try:
            rec = _lib.read_yaml(path, default={})
        except _lib.YamlError as exc:
            print(f"[ledger] skipping unreadable record {path.name}: {exc}", file=sys.stderr)
            continue
        if not isinstance(rec, dict) or not rec.get("date") or rec.get("mode") not in MODES:
            print(f"[ledger] skipping malformed record {path.name}", file=sys.stderr)
            continue
        rec = dict(rec)
        rec["_file"] = path.name
        runs.append(rec)
    runs.sort(key=lambda r: (str(r.get("date")), str(r.get("id", ""))))
    return runs


def last_run(runs: list[dict], mode: str) -> dict | None:
    """The most recent record with this mode, or None."""
    matching = [r for r in runs if r.get("mode") == mode]
    return matching[-1] if matching else None


def spent_signals(runs: list[dict]) -> set[str]:
    """Every story id any run has spent."""
    out: set[str] = set()
    for r in runs:
        for s in r.get("signals") or []:
            s = str(s).strip()
            if s:
                out.add(s)
    return out


def spent_directives(runs: list[dict]) -> set[str]:
    """Every editorial-directive issue URL a run record carries (`directive:`)."""
    return {str(r["directive"]).strip() for r in runs if str(r.get("directive") or "").strip()}


def improved_paths(runs: list[dict]) -> dict[str, str]:
    """path -> date of the most recent loop improvement to it."""
    out: dict[str, str] = {}
    for r in runs:
        if r.get("mode") == "improve" and r.get("path"):
            out[str(r["path"])] = str(r["date"])
    return out


def record(*, mode: str, section: str, path: str, title: str, signals: list[str],
           summary: str = "", pr: str = "", date=None, runs_dir: Path = _lib.RUNS_DIR,
           root: Path = _lib.ROOT, force: bool = False, directive: str = "") -> Path:
    """Write one run record and return its path. Refuses to overwrite. `directive`
    is the editorial-directive issue URL this run served, when the plan carried one."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    section = str(section).strip()
    if not section:
        raise ValueError("section is required")
    rel = str(path).strip().lstrip("./")
    if not rel:
        raise ValueError("path is required")
    if not (root / rel).exists():
        raise ValueError(f"path does not exist in the checkout: {rel} (record AFTER writing the content)")
    title = _lib.one_line(_lib.scrub(title), limit=160)
    if not title:
        raise ValueError("title is required")
    day = _lib.parse_date(date) if date else _lib.today()
    if day is None:
        raise ValueError(f"bad date: {date!r}")
    directive = _lib.scrub(str(directive or "")).strip()
    if directive and not ISSUE_URL_RE.match(directive):
        raise ValueError(f"not an issue URL: {directive!r}")
    clean = []
    for s in signals:
        s = str(s).strip()
        if s and s not in clean:
            clean.append(s)
    slug = _lib.slugify(title, limit=40) or "run"
    rec_id = f"{day.isoformat()}-{mode}-{slug}"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / f"{rec_id}.yml"
    if out.exists() and not force:
        raise FileExistsError(f"{out.name} already exists — a run is never overwritten")
    data = {
        "id": rec_id,
        "date": day.isoformat(),
        "mode": mode,
        "section": section,
        "path": rel,
        "title": title,
        "signals": clean,
        "summary": _lib.one_line(_lib.scrub(summary), limit=300),
        "pr": _lib.scrub(str(pr or "")).strip(),
    }
    if directive:
        data["directive"] = directive
    out.write_text(_lib.dump_yaml(data, header=RECORD_HEADER), encoding="utf-8")
    return out


def set_pr(run_id: str, url: str, runs_dir: Path = _lib.RUNS_DIR) -> Path:
    """Fill in the `pr:` line of an existing record (the URL only exists after the push)."""
    path = runs_dir / f"{run_id}.yml"
    if not path.exists():
        raise FileNotFoundError(f"no run record {path.name}")
    rec = _lib.read_yaml(path, default={})
    if not isinstance(rec, dict):
        raise ValueError(f"unreadable run record {path.name}")
    url = _lib.scrub(str(url)).strip()
    if not re.match(r"^https://github\.com/[^/\s]+/[^/\s]+/pull/\d+$", url):
        raise ValueError(f"not a pull request URL: {url!r}")
    rec["pr"] = url
    path.write_text(_lib.dump_yaml(rec, header=RECORD_HEADER), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _print_list(runs: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps([{k: v for k, v in r.items() if k != "_file"} for r in runs], indent=2))
        return
    if not runs:
        print("ledger: no runs recorded yet (the first run is due).")
        return
    print(f"ledger: {len(runs)} run(s)")
    print(f"  {'date':10}  {'mode':7}  {'section':10}  path")
    for r in runs:
        print(f"  {str(r['date']):10}  {str(r['mode']):7}  {str(r.get('section', '')):10}  {r.get('path', '')}")


def self_test() -> int:
    import tempfile

    failures: list[str] = []

    def check(name, got, want):
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        runs_dir = root / "_data" / "loop" / "runs"
        post = root / "pages" / "_posts" / "tech" / "2026-09-05-a-b.md"
        post.parent.mkdir(parents=True)
        post.write_text("---\ntitle: x\n---\nbody\n")
        p1 = record(mode="new", section="tech", path="pages/_posts/tech/2026-09-05-a-b.md",
                    title='Gating an "AI" loop: sk-ant-api03-abcdefghijklmnop', signals=["session:abc", "pr:38", "pr:38", ""],
                    summary="first", pr="https://github.com/x/y/pull/1", date="2026-09-05",
                    runs_dir=runs_dir, root=root)
        check("filename", p1.name, "2026-09-05-new-gating-an-ai-loop-sk-ant.yml")
        try:
            record(mode="new", section="tech", path="pages/_posts/tech/2026-09-05-a-b.md",
                   title='Gating an "AI" loop: sk-ant-api03-abcdefghijklmnop', signals=[], date="2026-09-05",
                   runs_dir=runs_dir, root=root)
            failures.append("overwrote an existing record")
        except FileExistsError:
            pass
        for bad in [dict(mode="bogus"), dict(section=""), dict(path="missing.md"), dict(date="nope")]:
            kwargs = dict(mode="improve", section="services", path="pages/_posts/tech/2026-09-05-a-b.md",
                          title="t", signals=[], date="2026-09-06", runs_dir=runs_dir, root=root)
            kwargs.update(bad)
            try:
                record(**kwargs)
                failures.append(f"accepted bad input {bad}")
            except ValueError:
                pass
        record(mode="improve", section="services", path="pages/_posts/tech/2026-09-05-a-b.md",
               title="Improve", signals=["day:2026-09-01"], date="2026-09-06", runs_dir=runs_dir, root=root)
        record(mode="new", section="muses", path="pages/_posts/tech/2026-09-05-a-b.md", title="Directed",
               signals=[], date="2026-09-07", runs_dir=runs_dir, root=root,
               directive="https://github.com/x/y/issues/70")
        for bad in ("https://github.com/x/y/pull/70", "javascript:alert(1)", "70"):
            try:
                record(mode="new", section="muses", path="pages/_posts/tech/2026-09-05-a-b.md", title="Bad directive",
                       signals=[], date="2026-09-08", runs_dir=runs_dir, root=root, directive=bad)
                failures.append(f"accepted bad directive {bad!r}")
            except ValueError:
                pass
        (runs_dir / "zz-broken.yml").write_text("mode: |\n  nope\n")
        (runs_dir / "zz-malformed.yml").write_text("hello: world\n")
        runs = load_runs(runs_dir)
        check("loads good records only", [r["id"] for r in runs],
              ["2026-09-05-new-gating-an-ai-loop-sk-ant", "2026-09-06-improve-improve", "2026-09-07-new-directed"])
        check("no directive -> no key", "directive" in runs[0], False)
        check("directive kept", runs[2]["directive"], "https://github.com/x/y/issues/70")
        check("spent directives", spent_directives(runs), {"https://github.com/x/y/issues/70"})
        check("scrubbed title", "abcdefghijklmnop" in runs[0]["title"], False)
        check("dedup signals", runs[0]["signals"], ["session:abc", "pr:38"])
        check("last new", last_run(runs, "new")["date"], "2026-09-07")
        check("last improve", last_run(runs, "improve")["date"], "2026-09-06")
        check("no such mode", last_run([], "new"), None)
        check("spent", spent_signals(runs), {"session:abc", "pr:38", "day:2026-09-01"})
        check("improved paths", improved_paths(runs), {"pages/_posts/tech/2026-09-05-a-b.md": "2026-09-06"})
        check("empty dir", load_runs(root / "nope"), [])
        set_pr("2026-09-06-improve-improve", "https://github.com/x/y/pull/7", runs_dir)
        check("set_pr", last_run(load_runs(runs_dir), "improve")["pr"], "https://github.com/x/y/pull/7")
        for bad in ("javascript:alert(1)", "https://example.com/pull/1"):
            try:
                set_pr("2026-09-06-improve-improve", bad, runs_dir)
                failures.append(f"set_pr accepted {bad!r}")
            except ValueError:
                pass

    if failures:
        print("ledger --self-test: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("ledger --self-test: PASS (record, refuse overwrite, validation, load, last, spent, cooldown, directive)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="The content loop's run ledger.")
    ap.add_argument("--list", action="store_true", help="list recorded runs (default)")
    ap.add_argument("--json", action="store_true", help="machine-readable output for --list")
    ap.add_argument("--last", choices=MODES, help="print the most recent run of this mode as JSON")
    ap.add_argument("--record", action="store_true", help="write a new run record")
    ap.add_argument("--mode", choices=MODES)
    ap.add_argument("--section")
    ap.add_argument("--path", help="the content file this run created or improved")
    ap.add_argument("--title")
    ap.add_argument("--signals", default="", help="comma-separated story ids this run spent")
    ap.add_argument("--summary", default="")
    ap.add_argument("--pr", default="", help="the pull request URL (may be added later)")
    ap.add_argument("--directive", default="", help="the editorial-directive issue URL this run served (plan mode `directive`)")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today, or LOOP_TODAY)")
    ap.add_argument("--force", action="store_true", help="allow overwriting an existing record")
    ap.add_argument("--set-pr", nargs=2, metavar=("RUN_ID", "URL"), help="link the pull request to an existing record")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.set_pr:
        try:
            out = set_pr(args.set_pr[0], args.set_pr[1])
        except (ValueError, FileNotFoundError) as exc:
            print(f"ledger: {exc}", file=sys.stderr)
            return 1
        print(str(out.relative_to(_lib.ROOT)))
        return 0
    if args.record:
        missing = [k for k in ("mode", "section", "path", "title") if not getattr(args, k)]
        if missing:
            ap.error(f"--record needs --{' --'.join(missing)}")
        try:
            out = record(mode=args.mode, section=args.section, path=args.path, title=args.title,
                         signals=[s for s in args.signals.split(",")], summary=args.summary,
                         pr=args.pr, date=args.date, force=args.force, directive=args.directive)
        except (ValueError, FileExistsError) as exc:
            print(f"ledger: {exc}", file=sys.stderr)
            return 1
        print(str(out.relative_to(_lib.ROOT)))
        return 0
    runs = load_runs()
    if args.last:
        r = last_run(runs, args.last)
        print(json.dumps({k: v for k, v in r.items() if k != "_file"}, indent=2) if r else "null")
        return 0
    _print_list(runs, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
