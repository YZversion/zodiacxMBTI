"""Streamlit entry: form → chart → report → optional tarot."""

from __future__ import annotations

import html
from datetime import date, time

import streamlit as st
import streamlit.components.v1 as components

from chart import PLACE_HINT, PlaceLookupError, build_chart
from interpret import stream_main_report, stream_tarot_report
from report_export import (
    DISCLAIMER,
    FontNotFoundError,
    PRIVACY,
    build_report_html,
    build_report_pdf,
    extract_section_4_advice,
    summary_headline,
)
from tarot import DrawnCard, draw_three
from tarot_ui import build_flip_html

MBTI_OPTIONS = [
    "不确定",
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
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Noto+Sans+SC:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --zx-bg: #05060a;
  --zx-text: #f4f1ea;
  --zx-muted: rgba(244, 241, 234, 0.62);
  --zx-accent: #c9a46c;
  --zx-glass: rgba(255, 255, 255, 0.08);
  --zx-border: rgba(255, 255, 255, 0.22);
  --zx-display: "Instrument Serif", "Noto Serif SC", Georgia, serif;
  --zx-body: "Space Grotesk", "Noto Sans SC", system-ui, sans-serif;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  color: var(--zx-text);
  font-family: var(--zx-body) !important;
}

[data-testid="stAppViewContainer"] {
  background-color: var(--zx-bg) !important;
  background-image:
    radial-gradient(1.4px 1.4px at 8% 12%, rgba(255,255,255,0.55) 0, transparent 2px),
    radial-gradient(1px 1px at 18% 48%, rgba(255,255,255,0.35) 0, transparent 2px),
    radial-gradient(1.6px 1.6px at 32% 22%, rgba(201,164,108,0.45) 0, transparent 2px),
    radial-gradient(1px 1px at 46% 68%, rgba(255,255,255,0.28) 0, transparent 2px),
    radial-gradient(1.3px 1.3px at 58% 16%, rgba(255,255,255,0.5) 0, transparent 2px),
    radial-gradient(1px 1px at 71% 42%, rgba(255,255,255,0.32) 0, transparent 2px),
    radial-gradient(1.5px 1.5px at 84% 28%, rgba(180,200,255,0.4) 0, transparent 2px),
    radial-gradient(1px 1px at 92% 74%, rgba(255,255,255,0.3) 0, transparent 2px),
    radial-gradient(1.2px 1.2px at 14% 82%, rgba(255,255,255,0.38) 0, transparent 2px),
    radial-gradient(1px 1px at 38% 90%, rgba(201,164,108,0.35) 0, transparent 2px),
    radial-gradient(1.4px 1.4px at 63% 86%, rgba(255,255,255,0.42) 0, transparent 2px),
    radial-gradient(1px 1px at 78% 58%, rgba(255,255,255,0.25) 0, transparent 2px),
    radial-gradient(ellipse 80% 55% at 70% 20%, rgba(70, 90, 160, 0.18), transparent 55%),
    radial-gradient(ellipse 70% 50% at 20% 80%, rgba(90, 60, 120, 0.14), transparent 50%),
    linear-gradient(165deg, #05060a 0%, #0a0d16 45%, #07080f 100%) !important;
  background-attachment: fixed !important;
}

[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(circle at 50% 35%, transparent 0%, rgba(0,0,0,0.35) 55%, rgba(0,0,0,0.72) 100%),
    linear-gradient(180deg, rgba(0,0,0,0.45) 0%, transparent 28%, transparent 62%, rgba(0,0,0,0.7) 100%);
}

[data-testid="stAppViewContainer"]::after {
  content: "";
  position: fixed;
  inset: -20%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.07;
  background-image: repeating-radial-gradient(
    circle at 17% 23%,
    rgba(255,255,255,0.85) 0 1px,
    transparent 1px 4px
  );
  background-size: 64px 64px;
  animation: zx-drift-grain 9s steps(8) infinite;
}

@keyframes zx-drift-grain {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-64px, 42px, 0); }
}

[data-testid="stHeader"] {
  background: rgba(5, 6, 10, 0.55) !important;
  backdrop-filter: blur(12px);
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
  letter-spacing: 0.01em;
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

/* Expander header: body font + room for the toggle arrow */
[data-testid="stExpander"] details summary,
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span:not([class*="icon"]):not([class*="arrow"]) {
  font-family: var(--zx-body) !important;
}
[data-testid="stExpander"] summary {
  gap: 0.65rem !important;
  align-items: center !important;
}
[data-testid="stExpander"] span[class*="arrow"],
[data-testid="stExpander"] span[class*="icon"],
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"],
span[class*="arrow_"] {
  font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
  flex: 0 0 auto !important;
  line-height: 1 !important;
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
    0 24px 60px rgba(0, 0, 0, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.16);
  overflow: hidden;
}
.zx-summary-card::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.16), transparent 40%),
    radial-gradient(circle at 86% 12%, rgba(201,164,108,0.2), transparent 32%);
}
.zx-summary-headline {
  position: relative;
  font-family: var(--zx-display);
  font-size: 1.45rem;
  line-height: 1.35;
  font-weight: 400;
  color: #fff;
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
  color: rgba(244, 241, 234, 0.92);
}
</style>
"""


def _inject_theme() -> None:
    # st.html keeps <style> out of visible markdown text
    st.html(THEME_CSS)


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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _fingerprint(
    birth_date: date,
    birth_time: time | None,
    time_unknown: bool,
    city: str,
    nation: str,
    mbti: str,
    user_question: str = "",
) -> tuple:
    t = None if time_unknown else (birth_time.hour, birth_time.minute) if birth_time else None
    return (
        birth_date.isoformat(),
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


def _render_svg(svg: str) -> None:
    # Square wheel chart; keep room so CN glyphs aren't crushed on mobile.
    wrapped = f"""
    <div style="width:100%;max-width:520px;margin:0 auto;aspect-ratio:1/1;
                overflow:hidden;background:#0a0d16;border-radius:12px;
                border:1px solid rgba(255,255,255,0.12);box-sizing:border-box;">
      <style>
        svg {{ width:100% !important; height:100% !important; display:block; }}
        text, tspan {{
          font-family: 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
        }}
      </style>
      {svg}
    </div>
    """
    components.html(wrapped, height=540, scrolling=False)


def _render_tarot_cards(cards: list[DrawnCard]) -> None:
    # Self-contained flip stage; interpretation text stays in Streamlit below.
    components.html(build_flip_html(cards), height=920, scrolling=False)


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

    st.title("星盘 × MBTI 性格解读")
    st.caption("一次性报告 · 不存账号 · 朋友圈 spike")

    # Country outside the form so「其他」能即时展开（form 内控件提交前不重跑）
    country_label = st.selectbox("出生国家", COUNTRY_LABELS, index=0)
    other_code = ""
    if country_label == "其他":
        other_code = st.text_input(
            "请填写两位国家代码",
            placeholder="例如 DE、FR",
            help="若列表中没有你的国家，填写两位字母代码（如德国 DE）。",
        )

    with st.form("birth_form"):
        birth_date = st.date_input(
            "出生日期",
            value=date(1995, 1, 1),
            min_value=date(1920, 1, 1),
            max_value=date.today(),
        )
        time_unknown = st.checkbox("不知道出生时间", value=False)
        birth_time = st.time_input(
            "出生时间",
            value=time(12, 0),
            disabled=time_unknown,
        )
        city = st.text_input(
            "出生城市",
            placeholder="Shanghai",
            help=PLACE_HINT,
        )
        mbti_raw = st.selectbox("MBTI", MBTI_OPTIONS, index=0)
        user_question = st.text_input(
            "最近在纠结的事（选填，报告会针对它展开）",
            placeholder="例：在纠结稳定的 A 和自由的 B 两份工作 / 一段关系要不要继续",
        )
        submitted = st.form_submit_button("生成解读", type="primary", use_container_width=True)

    if submitted:
        nation = _resolve_nation(country_label, other_code)
        if not city.strip():
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
                st.error(str(exc))
                st.stop()
            except Exception as exc:  # noqa: BLE001
                st.error(f"排盘失败：{exc}")
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
                st.error(f"解读生成失败：{exc}")
                st.stop()

            text = (report or "").strip() if isinstance(report, str) else str(report or "").strip()
            if not text:
                st.error("LLM 返回空内容，请稍后重试。")
                st.stop()
            st.session_state.report_text = text
            st.session_state.main_user_question = q
            # Prefill tarot question box with the same text (user can edit)
            st.session_state.tarot_question = q
            st.session_state.report_ready = True
            st.rerun()

    if st.session_state.report_ready and st.session_state.chart:
        chart = st.session_state.chart
        report_text = st.session_state.report_text or ""

        st.subheader("解读摘要")
        _render_summary_card(chart, report_text)

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
                help="含摘要、星盘图、报告与塔罗牌面。用浏览器打开后可「打印 → 另存为 PDF」。",
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
        with st.expander("展开查看完整星盘", expanded=False):
            st.caption("本命盘轮盘（暗色）。行星过密时度数可能仍会靠近，属排盘图常态。")
            _render_svg(chart.svg)

        st.subheader("解读报告")
        st.markdown(report_text)

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
                st.error(f"塔罗解读失败：{exc}")
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
            ):
                if k == "report_ready" or k == "tarot_streaming":
                    st.session_state[k] = False
                elif k == "main_user_question":
                    st.session_state[k] = ""
                else:
                    st.session_state[k] = None
            st.rerun()

        _footer()
    else:
        st.info(PLACE_HINT)
        _footer()


if __name__ == "__main__":
    main()
