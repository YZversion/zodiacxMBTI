"""Streamlit entry: form → chart → report → optional tarot."""

from __future__ import annotations

import base64
import html
from datetime import date, time

import streamlit as st

from chart import PLACE_HINT, PlaceLookupError, build_chart
from design_system import COLORS, css_variables
from interpret import generate_question_section, stream_main_report, stream_tarot_report
from persona_cards import (
    PERSONA_CARD_CSS,
    build_persona_card_html,
    build_persona_missing_html,
    build_persona_share_png,
    lookup_persona_card,
)
from report_export import (
    DISCLAIMER,
    FontNotFoundError,
    PRIVACY,
    build_report_html,
    build_report_pdf,
    extract_section_4_advice,
    has_complete_question_section,
    sanitize_main_report,
    split_main_and_extensions,
    split_numbered_sections,
    summary_headline,
    upsert_question_section,
)
from sun_preview import approximate_sun_sign_zh
from tarot import DrawnCard, draw_three
from tarot_ui import build_flip_html
from usage_stats import get_usage_stats, record_section_feedback, record_successful_report
from china_cities import resolve_china_city

MBTI_PLACEHOLDER = "请选择类型"
MBTI_TYPES = [
    "INTJ",
    "INTP",
    "ENTJ",
    "ENTP",
    "INFJ",
    "INFP",
    "ENFJ",
    "ENFP",
    "ISTJ",
    "ISFJ",
    "ESTJ",
    "ESFJ",
    "ISTP",
    "ISFP",
    "ESTP",
    "ESFP",
]
MBTI_OPTIONS = [MBTI_PLACEHOLDER, *MBTI_TYPES, "不确定"]

COUNTRY_LABELS = [
    "中国",
    "美国",
    "加拿大",
    "日本",
    "英国",
    "澳大利亚",
    "其他",
]
COUNTRY_TO_ISO = {
    "中国": "CN",
    "美国": "US",
    "加拿大": "CA",
    "日本": "JP",
    "英国": "GB",
    "澳大利亚": "AU",
}

THEME_CSS = """
<style>
:root {
  __ZX_DESIGN_TOKENS__
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  color: var(--zx-text);
  font-family: var(--zx-body) !important;
}

[data-testid="stAppViewContainer"] {
  background-color: var(--zx-bg) !important;
  background-image:
    radial-gradient(circle at 82% 13%, rgba(169, 96, 72, 0.20), transparent 25rem),
    radial-gradient(circle at 10% 88%, rgba(199, 175, 133, 0.10), transparent 22rem),
    linear-gradient(145deg, var(--zx-bg-deep) 0%, var(--zx-bg) 48%, var(--zx-surface) 100%) !important;
  background-size: auto, auto, auto !important;
  background-attachment: fixed !important;
}

[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    repeating-radial-gradient(
      circle at 84% 10%,
      transparent 0 3.7rem,
      rgba(199, 175, 133, 0.12) 3.74rem 3.79rem,
      transparent 3.83rem 6.7rem
    ),
    conic-gradient(
      from 22.5deg at 84% 10%,
      transparent 0 10deg,
      rgba(199, 175, 133, 0.10) 11deg 12deg,
      transparent 13deg 45deg
    ),
    linear-gradient(180deg, rgba(5, 11, 18, 0.08), rgba(5, 11, 18, 0.64));
}

[data-testid="stAppViewContainer"]::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.34;
  background-image:
    linear-gradient(
      115deg,
      transparent 0 48%,
      rgba(199, 175, 133, 0.075) 49% 50%,
      transparent 51%
    ),
    linear-gradient(
      65deg,
      transparent 0 48%,
      rgba(199, 175, 133, 0.05) 49% 50%,
      transparent 51%
    );
  background-size: 96px 96px;
  -webkit-mask-image: linear-gradient(to bottom, #000, transparent 74%);
  mask-image: linear-gradient(to bottom, #000, transparent 74%);
}

[data-testid="stHeader"] {
  display: none !important;
}

[data-testid="stMainBlockContainer"] {
  padding-top: 2.25rem !important;
  padding-bottom: 4rem !important;
}

[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] [data-testid="stMain"] {
  position: relative;
  z-index: 1;
}

h1, h2, h3,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
.stHeading {
  font-family: var(--zx-display) !important;
  color: var(--zx-text) !important;
  letter-spacing: 0.035em;
  text-shadow: 0 12px 34px rgba(0, 0, 0, 0.34);
}

[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
  display: flex;
  align-items: center;
  gap: 0.72rem;
}

[data-testid="stMarkdownContainer"] h2::before,
[data-testid="stMarkdownContainer"] h3::before,
[data-testid="stHeadingWithActionElements"] h2::before,
[data-testid="stHeadingWithActionElements"] h3::before {
  content: "";
  width: 0.58rem;
  height: 0.58rem;
  flex: 0 0 auto;
  border: 1px solid var(--zx-copper);
  box-shadow: inset 0 0 0 2px rgba(169, 96, 72, 0.12);
  transform: rotate(45deg);
}

[data-testid="stMarkdownContainer"] h2::after,
[data-testid="stMarkdownContainer"] h3::after,
[data-testid="stHeadingWithActionElements"] h2::after,
[data-testid="stHeadingWithActionElements"] h3::after {
  content: "";
  height: 1px;
  min-width: 2.5rem;
  flex: 1;
  background: linear-gradient(90deg, var(--zx-accent-strong), transparent);
  opacity: 0.56;
}

[data-testid="stMarkdownContainer"] h4 {
  padding-bottom: 0.55rem;
  border-bottom: 1px solid var(--zx-line);
  color: var(--zx-accent-strong) !important;
  font-family: var(--zx-display) !important;
  font-weight: 400;
  letter-spacing: 0.04em;
}

.zx-hero {
  position: relative;
  isolation: isolate;
  max-width: 46rem;
  padding: 2.35rem 0 2rem;
  overflow: hidden;
}
.zx-hero::after {
  content: "✦";
  position: absolute;
  top: -5.4rem;
  right: -2.8rem;
  z-index: -1;
  display: grid;
  place-items: center;
  width: 14.8rem;
  aspect-ratio: 1;
  border: 1px solid rgba(199, 175, 133, 0.28);
  border-radius: 50%;
  color: rgba(199, 175, 133, 0.52);
  font-family: Georgia, serif;
  font-size: 1.1rem;
  background:
    repeating-radial-gradient(
      circle,
      transparent 0 2.1rem,
      rgba(199, 175, 133, 0.18) 2.14rem 2.18rem,
      transparent 2.22rem 3.6rem
    ),
    repeating-conic-gradient(
      from 22.5deg,
      rgba(199, 175, 133, 0.16) 0 1deg,
      transparent 1deg 22.5deg
    );
  opacity: 0.72;
}
.zx-eyebrow {
  margin: 0 0 0.75rem;
  color: var(--zx-copper);
  font-family: var(--zx-data);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}
.zx-hero-rule {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  width: min(17.5rem, 76%);
  margin: 0.85rem 0 0.95rem;
  color: var(--zx-accent-strong);
}
.zx-hero-rule span {
  height: 1px;
  flex: 1;
  background: currentColor;
  opacity: 0.76;
}
.zx-hero-rule i {
  width: 0.55rem;
  aspect-ratio: 1;
  border: 1px solid currentColor;
  transform: rotate(45deg);
}
.zx-hero-title {
  margin: 0;
  color: var(--zx-text);
  font-family: var(--zx-display);
  font-size: clamp(2.8rem, 8vw, 5rem);
  font-weight: 400;
  letter-spacing: 0.045em;
  line-height: 1.06;
  text-wrap: balance;
  text-shadow: 0 18px 45px rgba(0, 0, 0, 0.44);
}
.zx-hero-title span {
  display: block;
}
.zx-hero-title b {
  color: var(--zx-copper);
  font-weight: 400;
}
.zx-hero-lede {
  max-width: 38rem;
  margin: 1.05rem 0 0;
  color: var(--zx-muted);
  font-size: 1rem;
  line-height: 1.75;
}
.zx-hero-lede strong {
  color: var(--zx-text);
  font-weight: 600;
}

/* Body copy only — never blanket-style `span` (breaks expander .arrow_ icon fonts) */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaption"],
.stCaption,
[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stSelectbox label,
.stDateInput label,
.stTimeInput label,
.stCheckbox label {
  font-family: var(--zx-body) !important;
}

[data-testid="stCaption"] {
  color: var(--zx-muted) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--zx-border) !important;
  border-radius: 14px !important;
  background:
    linear-gradient(135deg, rgba(199, 175, 133, 0.10), transparent 5.5rem),
    linear-gradient(315deg, rgba(169, 96, 72, 0.08), transparent 7rem),
    linear-gradient(145deg, rgba(16, 29, 43, 0.92), rgba(10, 21, 34, 0.76)) !important;
  box-shadow:
    0 22px 58px rgba(1, 6, 12, 0.34),
    inset 0 1px 0 rgba(238, 229, 212, 0.07);
  backdrop-filter: blur(14px);
}

[data-baseweb="input"],
[data-baseweb="select"] > div,
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stTimeInput"] [data-baseweb="input"] {
  background-color: var(--zx-surface) !important;
  border-color: var(--zx-border) !important;
}

[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
button:focus-visible,
summary:focus-visible {
  outline: 3px solid rgba(199, 175, 133, 0.92) !important;
  outline-offset: 2px !important;
  box-shadow: 0 0 0 5px rgba(9, 19, 31, 0.88) !important;
}

[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
  min-height: 2.8rem;
  border: 1px solid var(--zx-cta) !important;
  border-radius: 10px !important;
  background: var(--zx-cta) !important;
  color: var(--zx-cta-text) !important;
  font-weight: 700 !important;
  letter-spacing: 0.06em;
  box-shadow: 0 12px 28px rgba(2, 8, 16, 0.28);
}
[data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
  border-color: var(--zx-accent-strong) !important;
  background: var(--zx-copper) !important;
  color: var(--zx-text) !important;
  transform: translateY(-1px);
}

.zx-coordinate-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  margin: 0.5rem 0 0.8rem;
  overflow: hidden;
  border: 1px solid var(--zx-line);
  border-radius: 12px;
  background: var(--zx-line);
}
.zx-coordinate-cell {
  min-width: 0;
  padding: 0.72rem 0.78rem;
  background: rgba(5, 11, 18, 0.72);
}
.zx-coordinate-cell small {
  display: block;
  margin-bottom: 0.22rem;
  color: var(--zx-coordinate);
  font-family: var(--zx-data);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}
.zx-coordinate-cell strong {
  display: block;
  overflow: hidden;
  color: var(--zx-text);
  font-family: var(--zx-data);
  font-size: 0.82rem;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Expander arrows are Material Symbol ligatures (`_arrow_right`).
   Two failure modes produce the same mess:
   1) Our CJK font-family on summary spans breaks ligatures even if font loads.
   2) fonts.gstatic.com / Material CDN blocked or slow on China mobile.
   Fix: never restyle icon spans; hide the toggle glyph (label stays clickable). */
[data-testid="stExpander"] summary p {
  font-family: var(--zx-body) !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  font-family: var(--zx-body) !important;
}
[data-testid="stExpander"] summary {
  gap: 0.65rem !important;
  align-items: center !important;
}
[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"],
[data-testid="stExpander"] [data-testid="stIconMaterial"] {
  display: none !important;
}

/* §6 延伸探索: custom <details> — no Streamlit material-icon toggle */
.zx-ext-folds {
  display: grid;
  gap: 0.55rem;
  margin: 0.35rem 0 1rem;
}
.zx-ext-fold {
  border: 1px solid var(--zx-border);
  border-radius: 12px;
  background:
    linear-gradient(135deg, rgba(199, 175, 133, 0.07), transparent 5rem),
    var(--zx-glass);
  padding: 0.15rem 0.85rem 0.55rem;
}
.zx-ext-fold > summary {
  cursor: pointer;
  list-style: none;
  font-family: var(--zx-display);
  font-size: 1.02rem;
  color: var(--zx-accent-strong);
  padding: 0.7rem 0.1rem;
  line-height: 1.45;
}
.zx-ext-fold > summary::-webkit-details-marker { display: none; }
.zx-ext-fold > summary::after {
  content: " ▸";
  opacity: 0.7;
  font-size: 0.85em;
}
.zx-ext-fold[open] > summary::after { content: " ▾"; }
.zx-ext-body {
  color: var(--zx-text);
  font-family: var(--zx-body);
  font-size: 0.95rem;
  line-height: 1.65;
  padding: 0 0.1rem 0.55rem;
}

.zx-summary-card {
  position: relative;
  background: var(--zx-glass);
  border: 1px solid var(--zx-border);
  border-radius: 16px;
  padding: 1.2rem 1.2rem 1.25rem;
  margin: 0.4rem 0 1rem;
  color: var(--zx-text);
  box-sizing: border-box;
  max-width: 100%;
  overflow-wrap: anywhere;
  word-break: break-word;
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  box-shadow:
    0 24px 60px rgba(2, 8, 16, 0.42),
    inset 0 1px 0 rgba(231, 221, 201, 0.10);
  overflow: hidden;
}
.zx-summary-card::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(135deg, rgba(238,229,212,0.08), transparent 40%),
    radial-gradient(circle at 86% 12%, rgba(169,96,72,0.19), transparent 32%);
}
.zx-summary-headline {
  position: relative;
  font-family: var(--zx-display);
  font-size: 1.45rem;
  line-height: 1.35;
  font-weight: 400;
  color: var(--zx-text);
  margin: 0 0 0.8rem;
  text-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.zx-summary-advice-label {
  position: relative;
  font-family: var(--zx-body);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--zx-muted);
  margin: 0 0 0.4rem;
}
.zx-summary-advice {
  position: relative;
  font-family: var(--zx-body);
  font-size: 1.02rem;
  line-height: 1.6;
  margin: 0;
  color: var(--zx-text);
}

.zx-question-card {
  border-left: 3px solid var(--zx-copper);
  border-radius: 0 12px 12px 0;
  background: rgba(16, 29, 43, 0.78);
  padding: 0.9rem 1rem;
  margin: 0.35rem 0 1rem;
  box-shadow: 0 14px 36px rgba(2, 8, 16, 0.22);
}
.zx-question-card small {
  display: block;
  margin-bottom: 0.28rem;
  color: var(--zx-accent-strong);
  font-family: var(--zx-data);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
}
.zx-question-card p {
  margin: 0;
  color: var(--zx-text);
  font-family: var(--zx-body);
  font-size: 1rem;
  line-height: 1.65;
}

.zx-natal-chart {
  width: 100%;
  max-width: 640px;
  margin: 8px auto 1rem;
  box-sizing: border-box;
  overflow-x: hidden;
  border: 1px solid var(--zx-border);
  border-radius: 12px;
  background: var(--zx-surface);
}
.zx-natal-chart img {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  margin: 0 auto;
}

__ZX_PERSONA_CARD_CSS__

@media (max-width: 520px) {
  .zx-hero {
    padding-top: 1.3rem;
  }
  .zx-hero::after {
    top: -3.2rem;
    right: -5rem;
    width: 11rem;
    opacity: 0.48;
  }
  .zx-hero-title {
    font-size: 2.7rem;
    line-height: 1.14;
  }
  .zx-coordinate-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  [data-testid="stButton"] button[kind="primary"]:hover,
  [data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
    transform: none;
  }
}
</style>
""".replace("__ZX_DESIGN_TOKENS__", css_variables()).replace(
    "__ZX_PERSONA_CARD_CSS__", PERSONA_CARD_CSS
)


def _inject_theme() -> None:
    # Markdown's HTML path keeps global styles attached to the app DOM across
    # Streamlit reruns and is stable in the pinned Cloud runtime.
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def _secret(key: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(key, default) or default)
    except Exception:  # noqa: BLE001 — missing secrets.toml
        return default


def _require_api_key() -> str:
    key = _secret("OPENAI_API_KEY")
    if not key:
        st.error(
            "未配置 OPENAI_API_KEY。请在本地 `.streamlit/secrets.toml` "
            "或 Streamlit Cloud Secrets 中设置。"
        )
        st.stop()
    return key


def _friendly_error_message(exc: BaseException | str, *, kind: str = "api") -> str:
    """Map technical failures to short Chinese copy for end users."""
    text = str(exc)
    lower = text.lower()
    if kind == "place" or isinstance(exc, PlaceLookupError):
        return PLACE_HINT
    if any(token in lower for token in ("429", "rate limit", "too many requests", "quota")):
        return "系统访问有点忙，请稍候再试。"
    if any(
        token in lower
        for token in ("500", "502", "503", "504", "server error", "internal error", "overloaded")
    ):
        return "系统已躺下，晚安💤"
    if any(
        token in lower
        for token in ("401", "403", "invalid api key", "authentication", "unauthorized")
    ):
        return "解读服务暂时不可用，请稍后再试。"
    if "400" in lower or "bad request" in lower:
        if kind == "place" or "geonames" in lower or "city" in lower or "place" in lower:
            return PLACE_HINT
        return "系统访问频繁，请稍候再试。"
    if kind == "chart":
        return "排盘暂时没成功，请检查出生信息后重试。"
    return "解读服务暂时不可用，请稍后再试。"


def _show_user_error(exc: BaseException | str, *, kind: str = "api") -> None:
    st.error(_friendly_error_message(exc, kind=kind))
    with st.expander("技术详情", expanded=False):
        st.code(str(exc))


def _init_state() -> None:
    defaults = {
        "report_ready": False,
        "chart": None,
        "report_text": None,
        "tarot_cards": None,
        "tarot_text": None,
        "form_fingerprint": None,
        "tarot_streaming": False,
        "main_user_question": "",
        "section_feedback_votes": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _usage_bases() -> tuple[int, int]:
    try:
        total_base = int(_secret("GENERATION_COUNT_BASE", "0") or "0")
    except ValueError:
        total_base = 0
    try:
        question_base = int(_secret("QUESTION_COUNT_BASE", "0") or "0")
    except ValueError:
        question_base = 0
    return max(0, total_base), max(0, question_base)


def _usage_db_path():
    raw = _secret("USAGE_DB_PATH", "")
    if raw.strip():
        from pathlib import Path

        return Path(raw.strip())
    return None


def _render_usage_caption() -> None:
    total_base, question_base = _usage_bases()
    try:
        stats = get_usage_stats(
            db_path=_usage_db_path(),
            total_base=total_base,
            question_base=question_base,
        )
        st.caption(
            f"已生成 {stats.total} 次 · 其中 {stats.with_question} 次写下了想问的事"
        )
    except Exception:  # noqa: BLE001
        st.caption("已生成 — · 其中 — 次写下了想问的事")


def _generate_button_label(birth_date: date | None, mbti_raw: str) -> str:
    if not isinstance(birth_date, date):
        return "生成解读"
    if mbti_raw in (MBTI_PLACEHOLDER, "不确定", ""):
        return "生成解读"
    sun, _near = approximate_sun_sign_zh(birth_date)
    return f"解读我的{sun}×{mbti_raw}"


def _render_sun_hint(birth_date: date | None) -> None:
    if not isinstance(birth_date, date):
        return
    sun, near = approximate_sun_sign_zh(birth_date)
    if near:
        st.caption(
            f"大致太阳座：{sun}（换座日附近，提交后以排盘为准）"
        )
    else:
        st.caption(f"大致太阳座：{sun}（预览；提交后以排盘为准）")


def _render_combo_hint(birth_date: date | None, mbti_raw: str) -> None:
    if not isinstance(birth_date, date):
        return
    if mbti_raw in (MBTI_PLACEHOLDER, "不确定", ""):
        return
    sun, _near = approximate_sun_sign_zh(birth_date)
    st.caption(f"组合预告：{sun}×{mbti_raw}（提交后生成完整解读）")


def _render_city_hint(city: str, nation_label: str) -> None:
    if nation_label != "中国":
        return
    mapped = resolve_china_city(city)
    if mapped:
        st.caption(f"地点将按「{mapped}」解析")


def _feedback_vote_key(fingerprint, section: int) -> str:
    token = abs(hash(fingerprint)) % (10**12)
    return f"{token}|s{section}"


def _render_section_with_feedback(
    *,
    fingerprint,
    section_num: int,
    heading: str,
    body: str,
) -> None:
    if heading:
        st.markdown(f"{heading}\n\n{body}" if body else heading)
    elif body:
        st.markdown(body)
    if section_num < 1 or section_num > 5:
        return
    vote_key = _feedback_vote_key(fingerprint, section_num)
    votes = st.session_state.section_feedback_votes
    if vote_key in votes:
        label = "这段准" if votes[vote_key] else "这段不像我"
        st.caption(f"已记录：{label}")
        return
    token = abs(hash(fingerprint)) % (10**12)
    c1, c2 = st.columns(2)
    hit = c1.button(
        "这段准",
        key=f"fb_{token}_{section_num}_hit",
        use_container_width=True,
    )
    miss = c2.button(
        "这段不像我",
        key=f"fb_{token}_{section_num}_miss",
        use_container_width=True,
    )
    if hit or miss:
        is_hit = bool(hit)
        votes[vote_key] = is_hit
        st.session_state.section_feedback_votes = votes
        try:
            record_section_feedback(
                section=section_num,
                hit=is_hit,
                db_path=_usage_db_path(),
            )
        except Exception:  # noqa: BLE001
            pass
        st.rerun()


def _render_main_report_with_feedback(main_body: str, fingerprint) -> None:
    sections = split_numbered_sections(main_body)
    if not sections or (len(sections) == 1 and sections[0][0] == 0 and not sections[0][1]):
        st.markdown(main_body)
        return
    for num, heading, body in sections:
        _render_section_with_feedback(
            fingerprint=fingerprint,
            section_num=num,
            heading=heading,
            body=body,
        )


def _fingerprint(
    birth_date: date | None,
    birth_time: time | None,
    time_unknown: bool,
    city: str,
    nation: str,
    mbti: str,
    user_question: str = "",
) -> tuple:
    t = None if time_unknown else (birth_time.hour, birth_time.minute) if birth_time else None
    return (
        birth_date.isoformat() if isinstance(birth_date, date) else None,
        t,
        time_unknown,
        city.strip(),
        nation.strip().upper(),
        mbti,
        user_question.strip(),
    )


def _resolve_nation(country_label: str, other_code: str) -> str | None:
    if country_label != "其他":
        return COUNTRY_TO_ISO[country_label]
    code = (other_code or "").strip().upper()
    if len(code) != 2 or not code.isalpha():
        return None
    return code


def _render_summary_card(chart, report_text: str) -> None:
    advice = extract_section_4_advice(report_text or "")
    headline = html.escape(summary_headline(chart))
    advice_html = html.escape(advice).replace("\n", "<br>") if advice else ""
    body = f'<p class="zx-summary-headline">{headline}</p>'
    if advice_html:
        body += (
            '<p class="zx-summary-advice-label">当前阶段的一句话建议</p>'
            f'<p class="zx-summary-advice">{advice_html}</p>'
        )
    st.html(
        f'<div class="zx-summary-card">{body}</div>',
    )


def _render_question_card(question: str) -> None:
    value = (question or "").strip()
    if not value:
        return
    st.html(
        '<aside class="zx-question-card" aria-label="本次提交的问题">'
        "<small>本次问题</small>"
        f"<p>{html.escape(value)}</p>"
        "</aside>"
    )


def _render_persona_card(chart) -> None:
    card = lookup_persona_card(mbti=chart.mbti, sun_sign=chart.sun_sign)
    if card is None:
        st.html(build_persona_missing_html())
        return
    st.html(build_persona_card_html(card))
    try:
        cache_key = f"persona_png_{card.id}"
        png = st.session_state.get(cache_key)
        if not isinstance(png, (bytes, bytearray)) or not png:
            png = build_persona_share_png(card)
            st.session_state[cache_key] = png
        st.download_button(
            label="下载人设卡图片（PNG）",
            data=png,
            file_name=f"隐藏人格_{card.mbti}_{card.sun_zh}.png",
            mime="image/png",
            use_container_width=True,
            help="适合发微信/朋友圈；手机可保存后长按分享。",
            key="dl_persona_png",
        )
        st.caption("手机：下载后打开图片，长按即可转发。")
    except Exception:  # noqa: BLE001 — share is optional
        st.caption("人设卡图片暂不可用，仍可截图上方卡片。")


def _render_extension_folds(items: list[tuple[str, str]]) -> None:
    """Render §6 as HTML <details> to avoid Streamlit expander icon-font collisions."""
    blocks = ['<div class="zx-ext-folds">']
    for title, body in items:
        safe_title = html.escape(title)
        safe_body = html.escape(body or "（暂无解析）").replace("\n", "<br>")
        blocks.append(
            f'<details class="zx-ext-fold">'
            f"<summary>{safe_title}</summary>"
            f'<div class="zx-ext-body">{safe_body}</div>'
            f"</details>"
        )
    blocks.append("</div>")
    st.html("".join(blocks))


def _render_hero() -> None:
    st.html(
        """
        <section class="zx-hero">
          <p class="zx-eyebrow">Birth coordinate × personality type</p>
          <div class="zx-hero-rule" aria-hidden="true">
            <span></span><i></i><span></span>
          </div>
          <h1 class="zx-hero-title">
            <span>星盘 <b>×</b> MBTI</span>
          </h1>
          <p class="zx-hero-lede">
            把出生坐标与人格类型，读成一张属于你的命运角色牌。
            <strong>只讲矛盾，不讲套话。</strong>
          </p>
        </section>
        """
    )


def _render_coordinate_strip(
    *,
    birth_date: date | None,
    birth_time: time | None,
    time_unknown: bool,
    city: str,
    mbti: str,
) -> None:
    date_value = birth_date.isoformat() if isinstance(birth_date, date) else "DATE REQUIRED"
    if time_unknown:
        time_value = "UNKNOWN"
    elif birth_time is None:
        time_value = "TIME REQUIRED"
    else:
        time_value = birth_time.strftime("%H:%M")
    city_value = (city or "").strip().upper() or "CITY PENDING"
    mbti_value = "UNSET" if mbti in (MBTI_PLACEHOLDER, "不确定", "") else mbti
    cells = (
        ("DATE", date_value),
        ("LOCAL TIME", time_value),
        ("PLACE", city_value),
        ("TYPE", mbti_value),
    )
    body = "".join(
        '<div class="zx-coordinate-cell">'
        f"<small>{html.escape(label)}</small>"
        f"<strong>{html.escape(value)}</strong>"
        "</div>"
        for label, value in cells
    )
    st.html(f'<div class="zx-coordinate-strip" aria-label="当前输入摘要">{body}</div>')


def _render_svg(svg: str) -> None:
    # st.html DOMPurify strips raw <svg>; embed as base64 <img> instead.
    # Do not use st.iframe (mobile height="content" often measures 0px).
    if "<svg" not in (svg or "").lower():
        st.error("星盘图形格式无效，请重新生成。")
        return
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    st.html(
        '<div class="zx-natal-chart" role="img" aria-label="本命盘">'
        f'<img alt="本命盘" src="data:image/svg+xml;base64,{b64}" '
        'style="width:100%;height:auto;display:block"/>'
        "</div>"
    )


def _render_tarot_cards(cards: list[DrawnCard]) -> None:
    # Inline fragment participates in normal layout; no fixed-height iframe whitespace.
    st.html(build_flip_html(cards))


def _footer() -> None:
    st.divider()
    st.caption(PRIVACY)
    st.caption(DISCLAIMER)


def main() -> None:
    st.set_page_config(
        page_title="星盘 × MBTI 解读",
        page_icon="✦",
        layout="centered",
    )
    _init_state()
    _inject_theme()

    _render_hero()

    with st.container(border=True):
        st.markdown("#### 出生坐标")
        st.caption("日期、时间与地点共同决定星盘；不知道具体时间也可以继续。")
        country_label = st.selectbox("出生国家", COUNTRY_LABELS, index=0)
        other_code = ""
        if country_label == "其他":
            other_code = st.text_input(
                "请填写两位国家代码",
                placeholder="例如 DE、FR",
                help="若列表中没有你的国家，填写两位字母代码（如德国 DE）。",
            )
        birth_date = st.date_input(
            "出生日期（公历）",
            value=None,
            min_value=date(1920, 1, 1),
            max_value=date.today(),
            help="请填阳历（公历），与身份证/日历一致；暂不支持阴历换算。",
        )
        st.caption("请填阳历（公历），与身份证/日历一致；暂不支持阴历换算。")
        _render_sun_hint(birth_date if isinstance(birth_date, date) else None)
        time_unknown = st.checkbox("不知道出生时间", value=True)
        birth_time = st.time_input(
            "出生时间",
            value=time(12, 0),
            disabled=time_unknown,
            help="不确定时请勾选上方「不知道出生时间」，勿使用默认正午假装精确。",
        )
        if not time_unknown:
            st.caption("请确认出生时间（勿沿用默认值若与实际不符）。")
        city = st.text_input(
            "出生城市",
            placeholder="如 上海、西安，或 Shanghai、Xi'an",
            help=PLACE_HINT,
        )
        st.caption(
            "中国可直接填中文市名；拼音/英文也稳。"
            "山西 → Taiyuan / Shanxi；陕西 → Xi'an / Shaanxi（注意双 a）。"
        )
        _render_city_hint(city, country_label)

    with st.container(border=True):
        st.markdown("#### 人格参照")
        st.caption("MBTI 用来做交叉分析；不确定可以跳过。具体问题会在报告中单独展开。")
        user_question = st.text_area(
            "最近在纠结的事（选填，报告会针对它展开）",
            placeholder=(
                "例：在纠结稳定的 A 和自由的 B 两份工作；"
                "一段关系要不要继续；要不要回老家……\n"
                "写得越具体，§4 越不容易变成套话。"
            ),
            height=100,
        )
        mbti_raw = st.selectbox("MBTI", MBTI_OPTIONS, index=0)
        _render_combo_hint(
            birth_date if isinstance(birth_date, date) else None,
            mbti_raw,
        )
        _render_coordinate_strip(
            birth_date=birth_date if isinstance(birth_date, date) else None,
            birth_time=birth_time if isinstance(birth_time, time) else None,
            time_unknown=time_unknown,
            city=city,
            mbti=mbti_raw,
        )
        st.caption(f"{PRIVACY} · 免费 · 约 40 秒")
        btn_label = _generate_button_label(
            birth_date if isinstance(birth_date, date) else None,
            mbti_raw,
        )
        submitted = st.button(
            btn_label,
            type="primary",
            use_container_width=True,
            key="generate_report",
        )
        _render_usage_caption()

    if submitted:
        nation = _resolve_nation(country_label, other_code)
        if not isinstance(birth_date, date):
            st.error("请选择出生日期。")
            st.stop()
        if not time_unknown and not isinstance(birth_time, time):
            st.error("请选择出生时间，或勾选“不知道出生时间”。")
            st.stop()
        if mbti_raw == MBTI_PLACEHOLDER:
            st.error("请选择 MBTI 类型，或选「不确定」。")
            st.stop()
        if not (city or "").strip():
            st.error(PLACE_HINT)
            st.stop()
        if not nation:
            st.error("请填写有效的两位字母国家代码（例如 DE）。")
            st.stop()

        fp = _fingerprint(
            birth_date,
            birth_time,
            time_unknown,
            city,
            nation,
            mbti_raw,
            user_question,
        )
        if fp != st.session_state.form_fingerprint:
            st.session_state.report_ready = False
            st.session_state.chart = None
            st.session_state.report_text = None
            st.session_state.tarot_cards = None
            st.session_state.tarot_text = None
            st.session_state.tarot_streaming = False
            st.session_state.main_user_question = ""
            st.session_state.section_feedback_votes = {}
            for k in list(st.session_state.keys()):
                if isinstance(k, str) and k.startswith("persona_png_"):
                    del st.session_state[k]
            st.session_state.form_fingerprint = fp

        if not st.session_state.report_ready:
            api_key = _require_api_key()
            model = _secret("OPENAI_MODEL", "gpt-4o-mini")
            base_url = _secret("OPENAI_BASE_URL") or None
            geonames = _secret("GEONAMES_USERNAME") or None
            mbti = None if mbti_raw == "不确定" else mbti_raw
            q = (user_question or "").strip()

            try:
                with st.spinner("正在排盘…"):
                    chart = build_chart(
                        birth_date=birth_date,
                        birth_time=None if time_unknown else birth_time,
                        time_unknown=time_unknown,
                        city=city,
                        nation=nation,
                        mbti=mbti,
                        geonames_username=geonames,
                    )
            except PlaceLookupError as exc:
                _show_user_error(exc, kind="place")
                st.stop()
            except Exception as exc:  # noqa: BLE001
                _show_user_error(exc, kind="chart")
                st.stop()

            st.session_state.chart = chart
            st.subheader("解读报告")
            try:
                report = st.write_stream(
                    stream_main_report(
                        chart,
                        api_key=api_key,
                        model=model,
                        base_url=base_url,
                        user_question=q,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                _show_user_error(exc, kind="api")
                st.stop()

            text = (report or "").strip() if isinstance(report, str) else str(report or "").strip()
            text = sanitize_main_report(text)
            if not text:
                st.error("LLM 返回空内容，请稍后重试。")
                st.stop()
            if q and not has_complete_question_section(text):
                try:
                    with st.spinner("正在补全针对你问题的分析…"):
                        section = generate_question_section(
                            chart,
                            user_question=q,
                            api_key=api_key,
                            model=model,
                            base_url=base_url,
                        )
                    text = upsert_question_section(text, section)
                except Exception as exc:  # noqa: BLE001
                    _show_user_error(exc, kind="api")
                    st.stop()
            st.session_state.report_text = text
            st.session_state.main_user_question = q
            # Prefill tarot question box with the same text (user can edit)
            st.session_state.tarot_question = q
            try:
                record_successful_report(
                    has_question=bool(q),
                    db_path=_usage_db_path(),
                )
            except Exception:  # noqa: BLE001 — never block report
                pass
            st.session_state.report_ready = True
            st.rerun()

    if st.session_state.report_ready and st.session_state.chart:
        chart = st.session_state.chart
        report_text = sanitize_main_report(st.session_state.report_text or "")

        st.subheader("解读摘要")
        _render_question_card(st.session_state.main_user_question)
        _render_summary_card(chart, report_text)
        st.subheader("你的隐藏人格")
        _render_persona_card(chart)

        with st.expander("下载报告（可选）", expanded=False):
            try:
                page_html = build_report_html(
                    chart=chart,
                    report_text=report_text,
                    tarot_cards=st.session_state.tarot_cards,
                    tarot_text=st.session_state.tarot_text,
                )
                st.download_button(
                    label="下载完整页面（HTML）",
                    data=page_html.encode("utf-8"),
                    file_name="星盘MBTI完整报告.html",
                    mime="text/html; charset=utf-8",
                    use_container_width=True,
                    type="primary",
                    help="含摘要、人设卡、星盘图、报告与塔罗牌面。用浏览器打开后可「打印 → 另存为 PDF」。",
                    key="dl_full_html",
                )
            except Exception as exc:  # noqa: BLE001
                st.warning(f"完整页面导出失败：{exc}")

            try:
                pdf_bytes = build_report_pdf(
                    chart=chart,
                    report_text=report_text,
                    tarot_cards=st.session_state.tarot_cards,
                    tarot_text=st.session_state.tarot_text,
                )
                st.download_button(
                    label="下载文字版 PDF",
                    data=pdf_bytes,
                    file_name="星盘MBTI解读报告.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    help="轻量文字版，不含星盘大图与牌面图。",
                    key="dl_text_pdf",
                )
            except FontNotFoundError as exc:
                st.warning(str(exc))
            except Exception as exc:  # noqa: BLE001
                st.warning(f"PDF 生成失败：{exc}")

            st.caption("需要带图的 PDF：先下「完整页面」，浏览器打开后打印并另存为 PDF。")

        st.subheader("你的星盘")
        if chart.preface_notes:
            for note in chart.preface_notes:
                st.info(note)
        st.caption(
            f"地点解析为 {chart.resolved_city or chart.city}"
            + (f" · {chart.resolved_tz}" if chart.resolved_tz else "")
        )
        st.caption("本命盘轮盘（暗色）。行星过密时度数可能仍会靠近，属排盘图常态。")
        _render_svg(chart.svg)

        st.subheader("解读报告")
        main_body, ext_items = split_main_and_extensions(report_text)
        _render_main_report_with_feedback(
            main_body,
            st.session_state.form_fingerprint,
        )
        if ext_items:
            st.markdown("##### 延伸探索")
            st.caption("点开查看短解析（默认折叠）")
            _render_extension_folds(ext_items)

        st.subheader("再抽三张牌（可选）")
        st.caption("默认收起主漏斗之外的第二步；不想用可直接忽略。")
        question = st.text_input(
            "想问的事（可留空）",
            key="tarot_question",
            placeholder="例如：最近工作选择 / 感情沟通…",
        )

        if st.session_state.tarot_text and st.session_state.tarot_cards:
            _render_tarot_cards(st.session_state.tarot_cards)
            st.markdown(st.session_state.tarot_text)
        elif st.session_state.tarot_streaming and st.session_state.tarot_cards:
            _render_tarot_cards(st.session_state.tarot_cards)
            api_key = _require_api_key()
            model = _secret("OPENAI_MODEL", "gpt-4o-mini")
            base_url = _secret("OPENAI_BASE_URL") or None
            try:
                tarot_text = st.write_stream(
                    stream_tarot_report(
                        chart,
                        st.session_state.tarot_cards,
                        question=question,
                        api_key=api_key,
                        model=model,
                        base_url=base_url,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                st.session_state.tarot_streaming = False
                st.session_state.tarot_cards = None
                _show_user_error(exc, kind="api")
            else:
                text = (
                    (tarot_text or "").strip()
                    if isinstance(tarot_text, str)
                    else str(tarot_text or "").strip()
                )
                st.session_state.tarot_text = text
                st.session_state.tarot_streaming = False
                st.rerun()
        else:
            if st.button("抽三张牌并解读", use_container_width=True):
                st.session_state.tarot_cards = draw_three()
                st.session_state.tarot_text = None
                st.session_state.tarot_streaming = True
                st.rerun()

        if st.button("清除本次结果，重新填写", use_container_width=True):
            for k in (
                "report_ready",
                "chart",
                "report_text",
                "tarot_cards",
                "tarot_text",
                "form_fingerprint",
                "tarot_streaming",
                "main_user_question",
                "section_feedback_votes",
            ):
                if k == "report_ready" or k == "tarot_streaming":
                    st.session_state[k] = False
                elif k == "main_user_question":
                    st.session_state[k] = ""
                elif k == "section_feedback_votes":
                    st.session_state[k] = {}
                else:
                    st.session_state[k] = None
            for k in list(st.session_state.keys()):
                if isinstance(k, str) and k.startswith("persona_png_"):
                    del st.session_state[k]
            st.rerun()

        _footer()
    else:
        _footer()


if __name__ == "__main__":
    main()
