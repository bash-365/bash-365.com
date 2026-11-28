#!/usr/bin/env python3
"""Import zer0-CMS's reputation demo into this site: the data the interactive
replay on /services/reputation/ reads, and the screenshots the page shows.

The demo is zer0-CMS's `verify/demos/reputation/run.mjs`: the platform's
reputation agent reads and drafts for a fictional business on a simulated
Business Profile, and a person edits, approves and posts. Its evidence bundle
(`test/evidence/reputation-demo/`) holds `capture.json` and the screenshots.
This script turns them into:

- `_data/demos/reputation.json` — each review, what the agent read in it, its
  draft, what a person changed, and what was posted (stdlib only);
- `assets/images/reputation/*.webp` and the page's preview banner
  `assets/images/previews/reviews-and-reputation.jpg` — cropped and compressed
  with Pillow (`pip install pillow`; skipped with a note when it is missing).

Nothing is typed by hand: re-run the demo, then this, and commit both.

    python3 scripts/demos/import_reputation_demo.py --evidence ../zer0-cms/test/evidence/reputation-demo
"""

import argparse
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "_data" / "demos" / "reputation.json"
IMAGES = ROOT / "assets" / "images" / "reputation"
PREVIEW = ROOT / "assets" / "images" / "previews" / "reviews-and-reputation.jpg"

# The order the replay shows: the new reviews the agent drafted for, the old complaint a person asked about, then two
# it only read.
ORDER = [
    "qf-erik-noshow",
    "qf-sam-injection",
    "qf-ana-private",
    "qf-grace-burst",
    "WALK-IN",
    "qf-priya-fee",
    "qf-luis-spanish",
    "qf-dana-carpet",
]
# screenshot → (published name, crop box as (left, top, right, bottom) or None)
SHOTS = {
    "03-consent-screen.png": ("consent", (320, 0, 960, 380)),
    "07-profile-switches.png": ("profile-switches", (500, 0, 1280, 620)),
    "10-reviews-drafted.png": ("reviews-drafted", None),
    "11-review-no-show-drafted.png": ("review-no-show", (500, 0, 1280, 800)),
    "13-review-injection-drafted.png": ("review-injection", (500, 0, 1280, 800)),
    "14-review-private-details-drafted.png": ("review-private-details", (500, 0, 1280, 800)),
    "16-public-profile-after.png": ("public-profile-after", (0, 0, 1280, 1700)),
    "17-insights.png": ("insights", (230, 120, 1280, 960)),
    "18-profile-edit-applied.png": ("profile-edit", (500, 0, 1280, 720)),
    "19-api-calls.png": ("api-calls", (0, 0, 1280, 800)),
}


def added_words(draft: str, posted: str) -> str:
    """What a person inserted into the agent's draft, word for word (empty when they approved it as drafted)."""
    a, b = draft.split(), posted.split()
    inserted = []
    for op, _, _, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op in ("insert", "replace"):
            inserted.append(" ".join(b[j1:j2]))
    return " … ".join(inserted)


def review_row(r: dict) -> dict:
    analysis = r.get("analysis") or {}
    reply = next((x for x in r["replies"] if x["status"] == "posted"), None) or (r["replies"][-1] if r["replies"] else None)
    draft = (reply or {}).get("draft", "")
    posted = r.get("reply_on_google") or ""
    return {
        "id": r["id"],
        "rating": r["rating"],
        "reviewer": r["reviewer"],
        "text": r["text"],
        "sentiment": analysis.get("sentiment"),
        "topics": analysis.get("topics", []),
        "summary": analysis.get("summary", ""),
        "needs_attention": bool(analysis.get("needs_attention")),
        "language": analysis.get("language", ""),
        "draft": draft,
        "posted": posted if reply else "",
        "added": added_words(draft, posted) if reply and reply.get("edited_by_person") else "",
        "drafted_by": "the agent, for a new review" if (reply or {}).get("trigger") == "event"
        else "the agent, when a person asked" if reply else "",
        "model": (reply or {}).get("model") or "",
    }


def build(capture: dict) -> dict:
    by_id = {r["id"]: r for r in capture["reviews"]}
    walk_in = next((r for r in capture["reviews"] if r["id"].startswith("sim-")), None)
    rows = [review_row(walk_in if i == "WALK-IN" else by_id[i]) for i in ORDER if (walk_in if i == "WALK-IN" else by_id.get(i))]
    insights = capture["insights"]
    return {
        "_generated": "scripts/demos/import_reputation_demo.py from zer0-CMS test/evidence/reputation-demo/capture.json; "
        "do not edit by hand",
        "simulated": True,
        "business": {k: capture["business"].get(k, "") for k in ("title", "category", "description")},
        "guidance": capture["profile"]["reply_guidance"],
        "model": next((r["model"] for r in rows if r["model"]), ""),
        "reviews": rows,
        "insights": {
            "count": insights["count"],
            "average": insights["average"],
            "response_rate": insights["response_rate"],
            "unanswered": insights["unanswered"],
            "needs_attention": insights["needs_attention"],
            "sentiment": insights["sentiment"],
        },
    }


def images(evidence: Path) -> None:
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is not installed: images skipped (pip install pillow)", file=sys.stderr)
        return
    IMAGES.mkdir(parents=True, exist_ok=True)
    for source, (name, box) in SHOTS.items():
        with Image.open(evidence / source) as image:
            picture = image.convert("RGB")
            if box:
                picture = picture.crop(box)
            picture.save(IMAGES / f"{name}.webp", "WEBP", quality=82, method=6)
    with Image.open(evidence / "10-reviews-drafted.png") as image:
        banner = image.convert("RGB").crop((230, 60, 1280, 611)).resize((1200, 630), Image.LANCZOS)
        PREVIEW.parent.mkdir(parents=True, exist_ok=True)
        banner.save(PREVIEW, "JPEG", quality=85, optimize=True, progressive=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--evidence", type=Path, required=True, help="zer0-CMS's test/evidence/reputation-demo/")
    parser.add_argument("--no-images", action="store_true", help="write the data only")
    args = parser.parse_args(argv)
    capture = json.loads((args.evidence / "capture.json").read_text(encoding="utf-8"))
    if not capture.get("simulated"):
        print("refusing: capture.json is not from the simulated demo", file=sys.stderr)
        return 1
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(build(capture), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {DATA.relative_to(ROOT)}")
    if not args.no_images:
        images(args.evidence)
        print(f"wrote {IMAGES.relative_to(ROOT)}/ and {PREVIEW.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
