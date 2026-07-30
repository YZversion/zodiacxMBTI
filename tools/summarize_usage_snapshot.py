"""Print a short diagnosis from an exported usage_stats JSON snapshot.

Usage:
  python tools/summarize_usage_snapshot.py path/to/usage_stats_snapshot.json

Does not fetch Cloud data or write to the repo. Read-only stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Guardrails aligned with SHIP.md observation notes.
MIN_GENS_FOR_PROMPT = 50
MIN_SECTION_MISS_FOR_PROMPT = 5
MIN_GENS_FOR_RATE_CLAIM = 30


def summarize(path: Path) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 1

    total = int(data.get("total") or 0)
    with_q = int(data.get("with_question") or 0)
    without_q = int(data.get("without_question") or 0)
    exported = data.get("exported_at") or "(unknown)"
    sections = data.get("sections") or []

    q_pct = (100.0 * with_q / total) if total else 0.0
    print(f"exported_at: {exported}")
    print(f"total gens:  {total}")
    print(f"with_question: {with_q} ({q_pct:.0f}%)")
    print(f"without_question: {without_q}")
    print()
    print("section  hit  miss  rate   votes")
    print("-------  ---  ----  -----  -----")
    max_miss = 0
    total_votes = 0
    for row in sections:
        sec = int(row.get("section") or 0)
        hit = int(row.get("hit") or 0)
        miss = int(row.get("miss") or 0)
        votes = hit + miss
        total_votes += votes
        max_miss = max(max_miss, miss)
        rate = row.get("hit_rate")
        if rate is None and votes:
            rate = hit / votes
        rate_s = f"{float(rate):.0%}" if votes and rate is not None else "—"
        print(f"s{sec:<6}  {hit:<3}  {miss:<4}  {rate_s:<5}  {votes}")

    print()
    if total:
        print(f"feedback votes / gens: {total_votes} / {total}")
    print()
    print("--- verdict ---")
    if total < MIN_GENS_FOR_RATE_CLAIM:
        print(
            f"WARN: n={total} < {MIN_GENS_FOR_RATE_CLAIM} - do not treat hit rates as stable; "
            "do not rewrite MAIN_SYSTEM from this snapshot."
        )
    elif total < MIN_GENS_FOR_PROMPT or max_miss < MIN_SECTION_MISS_FOR_PROMPT:
        print(
            f"OK to track trends. Prompt churn still blocked until "
            f"total>={MIN_GENS_FOR_PROMPT} AND some section miss>={MIN_SECTION_MISS_FOR_PROMPT} "
            f"(now total={total}, max_miss={max_miss})."
        )
    else:
        print(
            "Sample large enough to consider a section prompt tweak - "
            "still prefer qualitative notes before editing MAIN_SYSTEM."
        )
    s1_votes = 0
    for row in sections:
        if int(row.get("section") or 0) == 1:
            s1_votes = int(row.get("hit") or 0) + int(row.get("miss") or 0)
            break
    if total and s1_votes < total:
        print(
            f"Note: s1 votes ({s1_votes}) < gens ({total}) - raising feedback tap rate "
            "beats rewriting copy."
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("snapshot", type=Path, help="Path to usage_stats_snapshot.json")
    args = p.parse_args(argv)
    return summarize(args.snapshot)


if __name__ == "__main__":
    raise SystemExit(main())
