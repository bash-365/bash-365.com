#!/usr/bin/env python3
"""PostHog server-side integration for bash-365.com.

Uses the personal API key (POSTHOG_API_KEY in .env) to talk to the PostHog REST
API — verifying the site is wired to the right project and posting deploy
annotations so releases line up with the analytics. Stdlib only.

Run as a directory:

    python3 scripts/features/posthog <command> [options]

Commands:
    verify       Confirm the site's client key matches the live project and
                 report the privacy-relevant settings (drift check).
    settings     Print the project's privacy-relevant settings.
    annotate     Post a deploy/release annotation to the project.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

import api
from config import Config
from net import PostHogHTTPError


def _utcnow_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def cmd_verify(cfg, args):
    cfg.require()
    project = api.get_project(cfg)
    live_token = project.get("api_token", "")
    print(f"project: {project.get('name')} (id {cfg.project_id}, region {cfg.region})")

    problems = 0
    # 1. The site must ship the live project's key, or events go elsewhere.
    if not cfg.client_key:
        print("  [WARN] could not read posthog.api_key from _config.yml")
    elif cfg.client_key == live_token:
        print("  [OK]   site client key matches this project")
    else:
        print("  [ERROR] site client key does NOT match this project — the site is "
              "sending events to a different (or wrong) project")
        problems += 1

    # 2. Privacy posture.
    def check(label, actual, want, hard=False):
        nonlocal problems
        ok = actual == want
        tag = "OK" if ok else ("ERROR" if hard else "WARN")
        if not ok and hard:
            problems += 1
        print(f"  [{tag}] {label}: {actual} (want {want})")

    check("IP anonymization (anonymize_ips)", project.get("anonymize_ips"), True)
    check("session recording opt-in", project.get("session_recording_opt_in"), False)
    if not project.get("ingested_event"):
        print("  [INFO] project has not ingested any event yet — deploy the corrected "
              "key and load the site to confirm data flows")
    print(f"  [INFO] event retention: {project.get('event_retention_months')} months "
          f"(enforced={project.get('events_retention_enforced')}) — plan-controlled on Cloud")

    print("verify: PASS" if problems == 0 else f"verify: FAIL ({problems} blocking issue(s))")
    return 1 if problems else 0


def cmd_settings(cfg, args):
    cfg.require()
    project = api.get_project(cfg)
    print(f"# PostHog project {cfg.project_id} ({project.get('name')})")
    for field in api.SETTINGS_FIELDS:
        if field in project:
            val = project[field]
            if field == "api_token" and isinstance(val, str):
                val = val[:12] + "…"
            print(f"  {field}: {val}")
    return 0


def cmd_annotate(cfg, args):
    cfg.require()
    content = args.content
    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8").strip()
    if not content:
        print("error: --content or --content-file is required")
        return 1
    date_marker = args.date or _utcnow_iso()
    if args.dry_run:
        print("dry-run: would create annotation")
        print(f"  content: {content}")
        print(f"  date_marker: {date_marker}")
        return 0
    result = api.create_annotation(cfg, content, date_marker=date_marker)
    print(f"annotation created (id {result.get('id')}) at {date_marker}")
    print(f"  {api.project_url(cfg)}/annotations")
    return 0


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dry-run", action="store_true")
    common.add_argument("--verbose", action="store_true")
    common.add_argument("--project-id", default=None)
    common.add_argument("--region", default=None, choices=["us", "eu"])

    parser = argparse.ArgumentParser(prog="posthog", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("verify", parents=[common], help="check project wiring + privacy settings")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("settings", parents=[common], help="print project settings")
    p.set_defaults(func=cmd_settings)

    p = sub.add_parser("annotate", parents=[common], help="post a deploy annotation")
    p.add_argument("--content", help="annotation text")
    p.add_argument("--content-file", help="read annotation text from a file")
    p.add_argument("--date", help="ISO-8601 date marker (default: now, UTC)")
    p.set_defaults(func=cmd_annotate)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    cfg = Config(project_id=args.project_id, region=args.region)
    try:
        return args.func(cfg, args)
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}")
        return 1
    except PostHogHTTPError as exc:
        print(f"PostHog API error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
