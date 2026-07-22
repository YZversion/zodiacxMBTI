"""Tarot presentation helpers (assets + flip HTML). Does not change draw logic."""

from __future__ import annotations

import base64
import html
from functools import lru_cache
from pathlib import Path

from design_system import css_variables
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
    """Self-contained HTML fragment: backs up, then sequential 3D flips."""
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

    tokens = css_variables()
    return f"""
<style>
  :root {{
    {tokens}
  }}
  .zx-tarot-stage {{
    margin: 0.4rem 0 1rem;
    padding: 1rem 0.75rem 1.1rem;
    border: 1px solid var(--zx-border);
    border-radius: 14px;
    background:
      linear-gradient(var(--zx-line) 1px, transparent 1px),
      linear-gradient(90deg, var(--zx-line) 1px, transparent 1px),
      linear-gradient(145deg, rgba(24,40,61,0.90), rgba(11,22,38,0.86));
    background-size: 28px 28px, 28px 28px, auto;
    color: var(--zx-text);
    font-family: var(--zx-body);
    box-sizing: border-box;
  }}
  .zx-flip-row {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 148px));
    justify-content: center;
    gap: 14px 16px;
    padding: 6px 0 2px;
    box-sizing: border-box;
  }}
  .zx-flip-item {{
    width: 100%;
    max-width: 100%;
    text-align: center;
    opacity: 0;
    animation: zx-fade-in 0.35s ease forwards;
  }}
  .zx-pos {{
    color: var(--zx-coordinate);
    font-family: var(--zx-data);
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 8px;
    letter-spacing: 0.12em;
  }}
  .zx-scene {{
    width: 100%;
    height: auto;
    aspect-ratio: 148 / 260;
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
    border: 1px solid rgba(231,221,201,0.20);
    box-shadow: 0 14px 30px rgba(2, 8, 16, 0.36);
  }}
  .zx-back {{
    background: linear-gradient(145deg, var(--zx-surface-strong), var(--zx-bg-deep));
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .zx-back-pattern {{
    width: 78%;
    height: 84%;
    border: 1px solid rgba(169, 198, 189, 0.48);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
      linear-gradient(var(--zx-line) 1px, transparent 1px),
      linear-gradient(90deg, var(--zx-line) 1px, transparent 1px),
      radial-gradient(circle at 50% 50%, rgba(127,167,155,0.24), transparent 58%);
    background-size: 14px 14px, 14px 14px, auto;
  }}
  .zx-back-pattern span {{
    color: var(--zx-accent-strong);
    font-size: 28px;
    opacity: 0.9;
  }}
  .zx-front {{
    transform: rotateY(180deg);
    background: var(--zx-text);
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
    color: var(--zx-text);
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
  .badge-up {{ background: var(--zx-cta); color: var(--zx-cta-text); }}
  .badge-rev {{ background: #e3b9b0; color: #4f1814; }}
  @keyframes zx-flip {{
    from {{ transform: rotateY(0deg); }}
    to {{ transform: rotateY(180deg); }}
  }}
  @keyframes zx-fade-in {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  @media (max-width: 520px) {{
    .zx-flip-row {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .zx-flip-item:last-child:nth-child(odd) {{
      grid-column: 1 / -1;
      justify-self: center;
      width: min(148px, 48%);
    }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .zx-flip-item {{
      opacity: 1;
      animation: none;
    }}
    .zx-card {{
      animation: none;
      transform: rotateY(180deg);
    }}
  }}
</style>
<div class="zx-tarot-stage">
  <div class="zx-flip-row">
    {''.join(items)}
  </div>
</div>
"""
