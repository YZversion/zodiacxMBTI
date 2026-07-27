"""Lookup + HTML render for MBTI × sun persona cards (offline JSON + zodiac masters)."""

from __future__ import annotations

import base64
import html
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
CARDS_PATH = ROOT / "persona_cards" / "persona_cards.json"
MASTERS_DIR = ROOT / "personapicture" / "zodiac_tarot_masters" / "v1"
MBTI_TAROT_ROOT = ROOT / "personapicture" / "mbti_tarot_cards"

# kerykeion may emit abbr (Ari) or full (Aries); cards use full English.
_SIGN_TO_EN: dict[str, str] = {
    "Ari": "Aries",
    "Aries": "Aries",
    "Tau": "Taurus",
    "Taurus": "Taurus",
    "Gem": "Gemini",
    "Gemini": "Gemini",
    "Can": "Cancer",
    "Cancer": "Cancer",
    "Leo": "Leo",
    "Vir": "Virgo",
    "Virgo": "Virgo",
    "Lib": "Libra",
    "Libra": "Libra",
    "Sco": "Scorpio",
    "Scorpio": "Scorpio",
    "Sag": "Sagittarius",
    "Sagittarius": "Sagittarius",
    "Cap": "Capricorn",
    "Capricorn": "Capricorn",
    "Aqu": "Aquarius",
    "Aquarius": "Aquarius",
    "Pis": "Pisces",
    "Pisces": "Pisces",
}

_SIGN_FOLDER: dict[str, str] = {
    "Aries": "aries",
    "Taurus": "taurus",
    "Gemini": "gemini",
    "Cancer": "cancer",
    "Leo": "leo",
    "Virgo": "virgo",
    "Libra": "libra",
    "Scorpio": "scorpio",
    "Sagittarius": "sagittarius",
    "Capricorn": "capricorn",
    "Aquarius": "aquarius",
    "Pisces": "pisces",
}

_MASTER_FILES: dict[str, str] = {
    "Aries": "01_aries_male.png",
    "Taurus": "02_taurus_female.png",
    "Gemini": "03_gemini_male.png",
    "Cancer": "04_cancer_female.png",
    "Leo": "05_leo_male.png",
    "Virgo": "06_virgo_female.png",
    "Libra": "07_libra_male.png",
    "Scorpio": "08_scorpio_female.png",
    "Sagittarius": "09_sagittarius_female.png",
    "Capricorn": "10_capricorn_male.png",
    "Aquarius": "11_aquarius_female.png",
    "Pisces": "12_pisces_male.png",
}

FOOTNOTE = "占比 = MBTI基准÷12（太阳座均匀假设），非精确普查"


@dataclass(frozen=True)
class PersonaCard:
    id: str
    nickname: str
    mbti: str
    sun_zh: str
    sun_en: str
    definition: str
    paradox: str
    exit: str
    pct: float
    pct_line: str
    rarity_label: str


def normalize_sun_en(sign: str) -> Optional[str]:
    key = (sign or "").strip()
    if not key:
        return None
    return _SIGN_TO_EN.get(key) or _SIGN_TO_EN.get(key.title())


def card_id(mbti: str, sun_en: str) -> str:
    return f"{mbti.strip().upper()}_{sun_en}"


@lru_cache(maxsize=1)
def _load_cards() -> dict[str, PersonaCard]:
    raw = json.loads(CARDS_PATH.read_text(encoding="utf-8"))
    out: dict[str, PersonaCard] = {}
    for row in raw.get("cards", []):
        card = PersonaCard(
            id=row["id"],
            nickname=row["nickname"],
            mbti=row["mbti"],
            sun_zh=row["sun_zh"],
            sun_en=row["sun_en"],
            definition=row["definition"],
            paradox=row["paradox"],
            exit=row["exit"],
            pct=float(row["pct"]),
            pct_line=row["pct_line"],
            rarity_label=row["rarity_label"],
        )
        out[card.id] = card
    return out


def lookup_persona_card(
    *,
    mbti: Optional[str],
    sun_sign: str,
) -> Optional[PersonaCard]:
    """Return the unique card for MBTI × sun, or None if MBTI unknown / missing."""
    if not mbti or mbti.strip() in ("", "不确定"):
        return None
    sun_en = normalize_sun_en(sun_sign)
    if not sun_en:
        return None
    return _load_cards().get(card_id(mbti, sun_en))


def master_image_path(sun_en: str) -> Optional[Path]:
    """Shared per-sign master (fallback when no MBTI-unique card exists)."""
    filename = _MASTER_FILES.get(sun_en)
    if not filename:
        return None
    path = MASTERS_DIR / filename
    return path if path.is_file() else None


def unique_mbti_card_path(*, mbti: str, sun_en: str) -> Optional[Path]:
    """Prefer `mbti_tarot_cards/{sign}/v1/*_{MBTI}_{Sun}_*.png` when present."""
    folder_name = _SIGN_FOLDER.get(sun_en)
    if not folder_name:
        return None
    mbti_u = (mbti or "").strip().upper()
    if not mbti_u or mbti_u == "不确定":
        return None
    folder = MBTI_TAROT_ROOT / folder_name / "v1"
    if not folder.is_dir():
        return None
    matches = sorted(folder.glob(f"*_{mbti_u}_{sun_en}_*.png"))
    if not matches:
        return None
    return matches[0]


def persona_art_path(*, mbti: str, sun_en: str) -> Optional[Path]:
    """MBTI×sign unique art first; else shared zodiac master."""
    unique = unique_mbti_card_path(mbti=mbti, sun_en=sun_en)
    if unique is not None:
        return unique
    return master_image_path(sun_en)


def _web_preview_bytes(path: Path, *, max_width: int = 900) -> tuple[bytes, str]:
    """Resize + JPEG for inline HTML (full PNG is ~3MB and often fails in st.html)."""
    from io import BytesIO

    from PIL import Image

    im = Image.open(path).convert("RGB")
    if im.width > max_width:
        height = int(im.height * (max_width / im.width))
        im = im.resize((max_width, height), Image.Resampling.LANCZOS)
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=82, optimize=True)
    return buf.getvalue(), "jpeg"


@lru_cache(maxsize=64)
def persona_art_data_uri(mbti: str, sun_en: str) -> Optional[str]:
    path = persona_art_path(mbti=mbti, sun_en=sun_en)
    if path is None:
        return None
    try:
        raw, subtype = _web_preview_bytes(path)
    except Exception:  # noqa: BLE001 — fall back to original bytes
        raw = path.read_bytes()
        subtype = "png" if path.suffix.lower() == ".png" else "jpeg"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/{subtype};base64,{b64}"


@lru_cache(maxsize=16)
def master_image_data_uri(sun_en: str) -> Optional[str]:
    """Backward-compatible: shared master only (no MBTI unique lookup)."""
    path = master_image_path(sun_en)
    if path is None:
        return None
    try:
        raw, subtype = _web_preview_bytes(path)
    except Exception:  # noqa: BLE001
        raw = path.read_bytes()
        subtype = "png"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/{subtype};base64,{b64}"


def build_persona_card_html(
    card: PersonaCard,
    *,
    include_image: bool = True,
) -> str:
    """Inline HTML fragment: screenshotable「你的隐藏人格」unit."""
    img_block = ""
    if include_image:
        uri = persona_art_data_uri(card.mbti, card.sun_en)
        if uri:
            alt = html.escape(f"{card.mbti} × {card.sun_zh}")
            img_block = (
                f'<div class="zx-persona-art">'
                f'<img src="{uri}" alt="{alt}" loading="lazy" />'
                f"</div>"
            )

    combo = html.escape(f"{card.mbti} × {card.sun_zh}")
    return f"""
<article class="zx-persona-card" aria-label="你的隐藏人格">
  {img_block}
  <div class="zx-persona-body">
    <p class="zx-persona-eyebrow">你的隐藏人格</p>
    <h2 class="zx-persona-nickname">{html.escape(card.nickname)}</h2>
    <p class="zx-persona-combo">{combo}</p>
    <div class="zx-persona-block">
      <p class="zx-persona-label">人设定义</p>
      <p class="zx-persona-text">{html.escape(card.definition)}</p>
    </div>
    <div class="zx-persona-block">
      <p class="zx-persona-label">一个具体矛盾</p>
      <p class="zx-persona-text">{html.escape(card.paradox)}</p>
    </div>
    <div class="zx-persona-block">
      <p class="zx-persona-label">出口（给你自己）</p>
      <p class="zx-persona-text">{html.escape(card.exit)}</p>
    </div>
    <p class="zx-persona-pct">{html.escape(card.pct_line)}</p>
    <p class="zx-persona-foot">{html.escape(FOOTNOTE)}</p>
  </div>
</article>
""".strip()


def build_persona_missing_html() -> str:
    """Hint when MBTI is unknown — no invented nickname."""
    return (
        '<aside class="zx-persona-missing" aria-label="人设卡提示">'
        "<p>选好 MBTI 类型后，这里会解锁你的专属怪名与人设卡。"
        "不确定时不做猜测。</p>"
        "</aside>"
    )


def build_persona_share_png(card: PersonaCard) -> bytes:
    """One-liner share card PNG (nickname + combo + short definition)."""
    from io import BytesIO

    from PIL import Image, ImageDraw, ImageFont

    from report_export import resolve_cjk_font

    width, height = 1080, 1350
    bg = (7, 16, 29)
    copper = (199, 175, 133)
    text_color = (232, 236, 241)
    muted = (148, 163, 184)
    accent = (169, 96, 72)

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    # Optional art on top third: MBTI×sign unique, else shared master
    master = persona_art_path(mbti=card.mbti, sun_en=card.sun_en)
    if master is not None:
        art = Image.open(master).convert("RGBA")
        art_h = 620
        art_w = int(art.width * (art_h / art.height))
        art = art.resize((art_w, art_h), Image.Resampling.LANCZOS)
        x = (width - art_w) // 2
        img.paste(art, (x, 40), art)

    font_path = str(resolve_cjk_font())
    font_sm = ImageFont.truetype(font_path, 28)
    font_md = ImageFont.truetype(font_path, 36)
    font_lg = ImageFont.truetype(font_path, 64)
    font_body = ImageFont.truetype(font_path, 34)

    y = 700 if master is not None else 120
    draw.text((72, y), "你的隐藏人格", fill=accent, font=font_sm)
    y += 48
    draw.text((72, y), card.nickname, fill=copper, font=font_lg)
    y += 88
    combo = f"{card.mbti} × {card.sun_zh}"
    draw.text((72, y), combo, fill=muted, font=font_md)
    y += 70

    # Wrap one-liner definition
    max_w = width - 144
    line = ""
    lines: list[str] = []
    for ch in card.definition.strip():
        trial = line + ch
        if draw.textlength(trial, font=font_body) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = ch
        if len(lines) >= 5:
            break
    if line and len(lines) < 5:
        lines.append(line)
    for ln in lines:
        draw.text((72, y), ln, fill=text_color, font=font_body)
        y += 48

    y = max(y + 40, height - 100)
    draw.text((72, y), "星盘 × MBTI", fill=muted, font=font_sm)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


PERSONA_CARD_CSS = """
.zx-persona-card {
  max-width: 420px;
  margin: 0.35rem auto 1.25rem;
  border: 1px solid var(--zx-border);
  border-radius: 16px;
  background: var(--zx-bg-deep);
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(2, 8, 16, 0.42);
  color: var(--zx-text);
}
.zx-persona-art {
  aspect-ratio: 3 / 5;
  overflow: hidden;
  background: var(--zx-bg-deep);
}
.zx-persona-art img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
}
.zx-persona-body {
  padding: 1.05rem 1.15rem 1.15rem;
  background:
    linear-gradient(180deg, rgba(7,16,29,0.2) 0%, var(--zx-surface) 28%);
}
.zx-persona-eyebrow {
  margin: 0 0 0.35rem;
  font-family: var(--zx-data);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--zx-accent-strong);
}
.zx-persona-nickname {
  margin: 0 0 0.35rem;
  font-family: var(--zx-display);
  font-size: clamp(1.55rem, 5vw, 1.9rem);
  font-weight: 400;
  line-height: 1.25;
  color: var(--zx-copper);
}
.zx-persona-combo {
  margin: 0 0 0.95rem;
  font-family: var(--zx-data);
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  color: var(--zx-coordinate);
}
.zx-persona-block { margin: 0 0 0.75rem; }
.zx-persona-label {
  margin: 0 0 0.28rem;
  font-family: var(--zx-body);
  font-size: 0.78rem;
  color: var(--zx-accent-strong);
}
.zx-persona-label::before {
  content: "▌";
  margin-right: 0.2rem;
  color: var(--zx-copper);
}
.zx-persona-text {
  margin: 0;
  font-family: var(--zx-body);
  font-size: 0.95rem;
  line-height: 1.65;
  color: var(--zx-text);
}
.zx-persona-pct {
  margin: 0.9rem 0 0.35rem;
  font-family: var(--zx-data);
  font-size: 0.78rem;
  color: var(--zx-muted);
}
.zx-persona-foot {
  margin: 0;
  font-family: var(--zx-body);
  font-size: 0.68rem;
  line-height: 1.45;
  color: var(--zx-muted);
  opacity: 0.85;
}
.zx-persona-missing {
  max-width: 420px;
  margin: 0.35rem auto 1.1rem;
  border-left: 3px solid var(--zx-coordinate);
  border-radius: 0 12px 12px 0;
  background: rgba(18, 31, 49, 0.72);
  padding: 0.85rem 1rem;
}
.zx-persona-missing p {
  margin: 0;
  font-family: var(--zx-body);
  font-size: 0.92rem;
  line-height: 1.55;
  color: var(--zx-muted);
}
@media (max-width: 520px) {
  .zx-persona-card { max-width: 100%; }
}
"""
