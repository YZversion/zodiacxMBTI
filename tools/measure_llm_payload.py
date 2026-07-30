"""Read-only LLM payload size report (does not call any API).

Prints character lengths for system / user prompts of main, §4 repair, and tarot.
Optional: build a real offline chart XML with --live-chart.

Usage:
  python tools/measure_llm_payload.py
  python tools/measure_llm_payload.py --live-chart
  python tools/measure_llm_payload.py --question "要不要换工作"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _fake_chart(*, question_xml: str = "<chart><point name='Sun' sign='Aries'/></chart>") -> Any:
    return SimpleNamespace(
        preface_notes=["出生时间已知，可使用上升与宫位信息。"],
        mbti="INTJ",
        resolved_city="Shenzhen",
        city="Shenzhen",
        nation="CN",
        resolved_tz="Asia/Shanghai",
        context_xml=question_xml,
    )


def _live_chart() -> Any:
    from datetime import date, time

    from chart import build_chart

    return build_chart(
        birth_date=date(1995, 4, 19),
        birth_time=time(7, 0),
        time_unknown=False,
        city="Shenzhen",
        nation="CN",
        mbti="INTJ",
        geonames_username=None,
    )


def _row(label: str, system: str, user: str, output_hint: str) -> None:
    print(f"=== {label} ===")
    print(f"  system_chars: {len(system)}")
    print(f"  user_chars:   {len(user)}")
    print(f"  input_chars:  {len(system) + len(user)}")
    print(f"  output_hint:  {output_hint} (prompt soft target; not measured)")
    print()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--live-chart",
        action="store_true",
        help="Build a real offline natal context_xml (no Geonames)",
    )
    p.add_argument(
        "--question",
        default="最近在纠结要不要换工作",
        help="Sample user question for main + §4 repair prompts",
    )
    args = p.parse_args(argv)

    from interpret import (
        MAIN_SYSTEM,
        QUESTION_SECTION_SYSTEM,
        TAROT_SYSTEM,
        _tarot_user_prompt,
        build_main_user_prompt,
        build_question_section_prompt,
    )
    from tarot import DrawnCard

    try:
        chart = _live_chart() if args.live_chart else _fake_chart()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR building chart: {exc}", file=sys.stderr)
        return 1

    xml_len = len(getattr(chart, "context_xml", "") or "")
    print(f"context_xml_chars: {xml_len}")
    print(f"question: {args.question!r}")
    print()

    main_user = build_main_user_prompt(chart, user_question=args.question)
    _row(
        "main_report",
        MAIN_SYSTEM,
        main_user,
        "700-1300 Chinese chars (§§1-5+6; +§4 if question)",
    )

    q_user = build_question_section_prompt(chart, user_question=args.question)
    _row(
        "section4_repair",
        QUESTION_SECTION_SYSTEM,
        q_user,
        "350-450 Chinese chars",
    )

    cards = [
        DrawnCard("大阿卡纳·愚者", "过去", False),
        DrawnCard("大阿卡纳·魔术师", "现在", True),
        DrawnCard("大阿卡纳·女祭司", "未来", False),
    ]
    tarot_user = _tarot_user_prompt(chart, cards, args.question)
    _row(
        "tarot",
        TAROT_SYSTEM,
        tarot_user,
        "500-650 Chinese chars",
    )

    print("--- quality note ---")
    print(
        "This tool never changes prompts or calls the API. "
        "Do not slim XML / system text without a human quality review."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
