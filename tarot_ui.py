"""Tarot presentation helpers (assets + flip HTML). Does not change draw logic."""

from __future__ import annotations

import base64
import html
from functools import lru_cache
from pathlib import Path

from tarot import MAJOR, DrawnCard

ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "tarot" / "rws"

_RANK_TO_N = {
    "王牌": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "侍从": 11,
    "骑士": 12,
    "王后": 13,
    "国王": 14,
}
_SUIT_PREFIX = {"权杖": "w", "圣杯": "c", "宝剑": "s", "星币": "p"}


def _build_name_to_file() -> dict[str, str]:
    mapping: dict[str, str] = {
        f"大阿卡纳·{name}": f"{i}.jpg" for i, name in enumerate(MAJOR)
    }
    for suit_zh, prefix in _SUIT_PREFIX.items():
        for rank, num in _RANK_TO_N.items():
            mapping[f"{suit_zh}{rank}"] = f"{prefix}{num}.jpg"
    return mapping


NAME_TO_FILE = _build_name_to_file()


@lru_cache(maxsize=96)
def _image_data_uri(filename: str) -> str:
    path = ASSETS_DIR / filename
    raw = path.read_bytes()
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif raw[:2] == b"\xff\xd8":
        mime = "image/jpeg"
    else:
        mime = "image/jpeg"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def card_face_data_uri(card_name: str) -> str:
    filename = NAME_TO_FILE.get(card_name)
    if not filename:
        raise KeyError(f"No asset mapping for card: {card_name}")
    return _image_data_uri(filename)


def build_flip_html(cards: list[DrawnCard]) -> str:
    """Self-contained HTML/CSS: backs up, then sequential 3D flips."""
    items: list[str] = []
    for i, card in enumerate(cards):
        delay = f"{i * 0.4:.1f}s"
        uri = card_face_data_uri(card.name)
        rev_cls = " is-reversed" if card.reversed else ""
        badge = "逆位" if card.reversed else "正位"
        badge_cls = "badge-rev" if card.reversed else "badge-up"
        items.append(
            f"""
            <div class="zx-flip-item" style="animation-delay:{delay}">
              <div class="zx-pos">{html.escape(card.position)}</div>
              <div class="zx-scene">
                <div class="zx-card" style="animation-delay:{delay}">
                  <div class="zx-face zx-back" aria-hidden="true">
                    <div class="zx-back-pattern"><span>✦</span></div>
                  </div>
                  <div class="zx-face zx-front{rev_cls}">
                    <img src="{uri}" alt="{html.escape(card.name)}" />
                  </div>
                </div>
              </div>
              <div class="zx-meta">
                <div class="zx-name">{html.escape(card.name)}</div>
                <span class="zx-badge {badge_cls}">{badge}</span>
              </div>
            </div>
            """
        )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8" />
<style>
  html, body {{
    margin: 0; padding: 0;
    background: transparent;
    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    color: #1c1b19;
  }}
  .zx-flip-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 14px 16px;
    padding: 6px 4px 10px;
    box-sizing: border-box;
  }}
  .zx-flip-item {{
    width: 148px;
    max-width: 100%;
    text-align: center;
    opacity: 0;
    animation: zx-fade-in 0.35s ease forwards;
  }}
  .zx-pos {{
    font-size: 12px;
    color: #6b655c;
    margin-bottom: 8px;
    letter-spacing: 0.06em;
  }}
  .zx-scene {{
    width: 148px;
    height: 260px;
    margin: 0 auto;
    perspective: 1100px;
  }}
  .zx-card {{
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transform: rotateY(0deg);
    animation: zx-flip 0.85s ease forwards;
  }}
  .zx-face {{
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 8px 18px rgba(44, 74, 110, 0.18);
  }}
  .zx-back {{
    background: linear-gradient(145deg, #2c4a6e 0%, #1e334d 55%, #3a5f86 100%);
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .zx-back-pattern {{
    width: 78%;
    height: 84%;
    border: 1px solid rgba(247, 244, 239, 0.35);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(circle at 30% 30%, rgba(247,244,239,0.18) 0 1px, transparent 2px),
      radial-gradient(circle at 70% 60%, rgba(247,244,239,0.14) 0 1px, transparent 2px);
    background-size: 12px 12px, 16px 16px;
  }}
  .zx-back-pattern span {{
    color: #f7f4ef;
    font-size: 28px;
    opacity: 0.9;
  }}
  .zx-front {{
    transform: rotateY(180deg);
    background: #f7f4ef;
  }}
  .zx-front img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}
  .zx-front.is-reversed img {{
    transform: rotate(180deg);
  }}
  .zx-meta {{
    margin-top: 10px;
  }}
  .zx-name {{
    font-size: 14px;
    font-weight: 650;
    line-height: 1.35;
    margin-bottom: 6px;
  }}
  .zx-badge {{
    display: inline-block;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 999px;
    font-weight: 600;
  }}
  .badge-up {{ background: #dceee3; color: #1f6b45; }}
  .badge-rev {{ background: #f3d9d4; color: #8a2f2a; }}
  @keyframes zx-flip {{
    from {{ transform: rotateY(0deg); }}
    to {{ transform: rotateY(180deg); }}
  }}
  @keyframes zx-fade-in {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  @media (max-width: 420px) {{
    .zx-flip-item, .zx-scene {{ width: 160px; }}
    .zx-scene {{ height: 282px; }}
  }}
</style></head>
<body>
  <div class="zx-flip-row">
    {"".join(items)}
  </div>
</body></html>"""
