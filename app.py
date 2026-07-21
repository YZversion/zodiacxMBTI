"""Streamlit entry: form → chart → report → optional tarot."""

from __future__ import annotations

from datetime import date, time

import streamlit as st
import streamlit.components.v1 as components

from chart import PLACE_HINT, PlaceLookupError, build_chart
from interpret import generate_main_report, generate_tarot_report
from tarot import draw_three

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

PRIVACY = "出生信息仅用于本次计算，不存储、不留日志。"
DISCLAIMER = (
    "本报告由 AI 生成，内容仅供娱乐与自我探索，不构成心理、医疗或重大决策建议。"
)


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
) -> tuple:
    t = None if time_unknown else (birth_time.hour, birth_time.minute) if birth_time else None
    return (birth_date.isoformat(), t, time_unknown, city.strip(), nation.strip().upper(), mbti)


def _render_svg(svg: str) -> None:
    # Full chart SVG is large; iframe avoids Streamlit markdown size quirks.
    components.html(
        f'<div style="width:100%;overflow:auto;background:#fff">{svg}</div>',
        height=720,
        scrolling=True,
    )


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

    st.title("星盘 × MBTI 性格解读")
    st.caption("一次性报告 · 不存账号 · 朋友圈 spike")

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
        nation = st.text_input(
            "国家代码（ISO，两位）",
            value="CN",
            help="中国填 CN，美国填 US。与城市一起交给 GeoNames 解析。",
        )
        mbti_raw = st.selectbox("MBTI", MBTI_OPTIONS, index=0)
        submitted = st.form_submit_button("生成解读", type="primary", use_container_width=True)

    if submitted:
        if not city.strip():
            st.error(PLACE_HINT)
            st.stop()

        fp = _fingerprint(birth_date, birth_time, time_unknown, city, nation, mbti_raw)
        # New inputs → clear cached report / tarot so we don't show stale results
        if fp != st.session_state.form_fingerprint:
            st.session_state.report_ready = False
            st.session_state.chart = None
            st.session_state.report_text = None
            st.session_state.tarot_cards = None
            st.session_state.tarot_text = None
            st.session_state.form_fingerprint = fp

        if not st.session_state.report_ready:
            api_key = _require_api_key()
            model = _secret("OPENAI_MODEL", "gpt-4o-mini")
            base_url = _secret("OPENAI_BASE_URL") or None
            geonames = _secret("GEONAMES_USERNAME") or None
            mbti = None if mbti_raw == "不确定" else mbti_raw

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

            try:
                with st.spinner("正在排盘解读（约 30–60 秒）…"):
                    report = generate_main_report(
                        chart,
                        api_key=api_key,
                        model=model,
                        base_url=base_url,
                    )
            except Exception as exc:  # noqa: BLE001
                st.error(f"解读生成失败：{exc}")
                st.stop()

            st.session_state.chart = chart
            st.session_state.report_text = report
            st.session_state.report_ready = True

    if st.session_state.report_ready and st.session_state.chart:
        chart = st.session_state.chart
        st.subheader("你的星盘")
        if chart.preface_notes:
            for note in chart.preface_notes:
                st.info(note)
        st.caption(
            f"地点解析为 {chart.resolved_city or chart.city}"
            + (f" · {chart.resolved_tz}" if chart.resolved_tz else "")
        )
        _render_svg(chart.svg)

        st.subheader("解读报告")
        st.markdown(st.session_state.report_text)

        st.subheader("再抽三张牌（可选）")
        st.caption("默认收起主漏斗之外的第二步；不想用可直接忽略。")
        question = st.text_input(
            "想问的事（可留空）",
            key="tarot_question",
            placeholder="例如：最近工作选择 / 感情沟通…",
        )

        if st.session_state.tarot_text:
            cards = st.session_state.tarot_cards or []
            st.write("抽牌结果：")
            for c in cards:
                st.write(f"- {c.label_zh()}")
            st.markdown(st.session_state.tarot_text)
        else:
            if st.button("抽三张牌并解读", use_container_width=True):
                api_key = _require_api_key()
                model = _secret("OPENAI_MODEL", "gpt-4o-mini")
                base_url = _secret("OPENAI_BASE_URL") or None
                cards = draw_three()
                try:
                    with st.spinner("正在结合星盘解读牌面…"):
                        tarot_text = generate_tarot_report(
                            chart,
                            cards,
                            question=question,
                            api_key=api_key,
                            model=model,
                            base_url=base_url,
                        )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"塔罗解读失败：{exc}")
                else:
                    st.session_state.tarot_cards = cards
                    st.session_state.tarot_text = tarot_text
                    st.rerun()

        if st.button("清除本次结果，重新填写", use_container_width=True):
            for k in (
                "report_ready",
                "chart",
                "report_text",
                "tarot_cards",
                "tarot_text",
                "form_fingerprint",
            ):
                st.session_state[k] = False if k == "report_ready" else None
            st.rerun()

        _footer()
    else:
        st.info(PLACE_HINT)
        _footer()


if __name__ == "__main__":
    main()
