"""Natal chart computation via kerykeion."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import Optional

from kerykeion import AstrologicalSubjectFactory, ChartDataFactory, to_context
from kerykeion.charts.chart_drawer import ChartDrawer

from china_cities import maybe_resolve_city

SIGN_ZH = {
    "Ari": "白羊",
    "Aries": "白羊",
    "Tau": "金牛",
    "Taurus": "金牛",
    "Gem": "双子",
    "Gemini": "双子",
    "Can": "巨蟹",
    "Cancer": "巨蟹",
    "Leo": "狮子",
    "Vir": "处女",
    "Virgo": "处女",
    "Lib": "天秤",
    "Libra": "天秤",
    "Sco": "天蝎",
    "Scorpio": "天蝎",
    "Sag": "射手",
    "Sagittarius": "射手",
    "Cap": "摩羯",
    "Capricorn": "摩羯",
    "Aqu": "水瓶",
    "Aquarius": "水瓶",
    "Pis": "双鱼",
    "Pisces": "双鱼",
}

PLACE_HINT = (
    "中国常用市名可直接填中文（如 上海、西安、太原）；"
    "或用拼音/英文（Shanghai、Xi'an、Taiyuan）。"
    "山西用 Taiyuan / Shanxi，陕西用 Xi'an / Shaanxi（双 a）。"
    "解析失败可改输附近更大城市，误差可忽略。"
)


class PlaceLookupError(Exception):
    """GeoNames could not resolve the city."""


@dataclass
class MoonAmbiguity:
    sign_at_start: str
    sign_at_end: str

    @property
    def message_zh(self) -> str:
        a = sign_to_zh(self.sign_at_start)
        b = sign_to_zh(self.sign_at_end)
        return (
            f"你出生当天月亮由{a}座进入{b}座，因出生时间未知无法确定；"
            f"以下对两种可能各做简述。"
        )


@dataclass
class ChartResult:
    subject_name: str
    birth_date: date
    birth_time: Optional[time]
    time_unknown: bool
    city: str
    nation: str
    mbti: Optional[str]
    context_xml: str
    svg: str
    moon_ambiguity: Optional[MoonAmbiguity] = None
    preface_notes: list[str] = field(default_factory=list)
    resolved_city: str = ""
    resolved_tz: str = ""
    sun_sign: str = ""
    moon_sign: str = ""
    asc_sign: str = ""


def sign_to_zh(sign: str) -> str:
    return SIGN_ZH.get(sign, sign)


def _subject(
    *,
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    city: str,
    nation: str,
    geonames_username: Optional[str],
):
    kwargs = dict(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city.strip(),
        nation=nation.strip().upper(),
        online=True,
        suppress_geonames_warning=True,
    )
    if geonames_username:
        kwargs["geonames_username"] = geonames_username
    try:
        return AstrologicalSubjectFactory.from_birth_data(**kwargs)
    except Exception as exc:  # noqa: BLE001 — surface as place error for UI
        raise PlaceLookupError(f"{PLACE_HINT}（原始错误：{exc}）") from exc


def _moon_signs_for_day(
    *,
    birth_date: date,
    city: str,
    nation: str,
    geonames_username: Optional[str],
) -> tuple[str, str]:
    start = _subject(
        name="MoonStart",
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=0,
        minute=0,
        city=city,
        nation=nation,
        geonames_username=geonames_username,
    )
    # End of civil day: next calendar day 00:00 (plan: 0:00 vs 24:00)
    end_day = birth_date + timedelta(days=1)
    end = _subject(
        name="MoonEnd",
        year=end_day.year,
        month=end_day.month,
        day=end_day.day,
        hour=0,
        minute=0,
        city=city,
        nation=nation,
        geonames_username=geonames_username,
    )
    return start.moon.sign, end.moon.sign


def _strip_houses_and_angles(xml: str) -> str:
    """Remove house/angle ground truth when birth time is unknown."""
    xml = re.sub(r"<houses>.*?</houses>", "", xml, flags=re.DOTALL)
    for point in ("Ascendant", "Medium_Coeli", "Descendant", "Imum_Coeli"):
        xml = re.sub(
            rf'<point name="{point}"[^/]*/>',
            "",
            xml,
        )
        xml = re.sub(
            rf'<point name="{point}"[^>]*>.*?</point>',
            "",
            xml,
            flags=re.DOTALL,
        )
    # Drop house= attributes on remaining points so the model is not misled
    xml = re.sub(r'\s+house="[^"]*"', "", xml)
    return xml


def _prepare_chart_svg(svg: str) -> str:
    """Inject CJK-safe fonts so CN labels don't collide with Latin metrics."""
    style = (
        "<style type='text/css'><![CDATA[\n"
        "  text, tspan {\n"
        "    font-family: 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC',"
        " 'Helvetica Neue', Arial, sans-serif !important;\n"
        "  }\n"
        "]]></style>\n"
    )
    if "<svg" not in svg or "Noto Sans SC" in svg:
        return svg
    # Insert style immediately after the opening <svg ...> tag
    return re.sub(r"(<svg\b[^>]*>)", r"\1" + style, svg, count=1, flags=re.IGNORECASE)


def _svg_for_subject(subject) -> str:
    chart_data = ChartDataFactory.create_natal_chart_data(subject)
    drawer = ChartDrawer(
        chart_data=chart_data,
        theme="dark",
        chart_language="CN",
        custom_title="本命盘",
        show_house_position_comparison=False,
        show_cusp_position_comparison=False,
        show_degree_indicators=True,
        show_aspect_icons=False,
    )
    # Wheel-only: full chart's CN info tables overlap badly on mobile scale
    svg = drawer.generate_wheel_only_svg_string()
    return _prepare_chart_svg(svg)


def build_chart(
    *,
    birth_date: date,
    birth_time: Optional[time],
    time_unknown: bool,
    city: str,
    nation: str,
    mbti: Optional[str],
    geonames_username: Optional[str] = None,
    subject_name: str = "本命",
) -> ChartResult:
    if not city or not city.strip():
        raise PlaceLookupError(PLACE_HINT)

    nation = (nation or "CN").strip().upper() or "CN"
    city_input = city.strip()
    city_lookup = maybe_resolve_city(city_input, nation)
    notes: list[str] = []
    moon_ambiguity: Optional[MoonAmbiguity] = None

    if time_unknown or birth_time is None:
        hour, minute = 12, 0
        time_unknown = True
        notes.append(
            "因出生时间未知，本报告不含上升星座与宫位分析；行星落座按当日 12:00 计算。"
        )
        start_sign, end_sign = _moon_signs_for_day(
            birth_date=birth_date,
            city=city_lookup,
            nation=nation,
            geonames_username=geonames_username,
        )
        if start_sign != end_sign:
            moon_ambiguity = MoonAmbiguity(start_sign, end_sign)
            notes.append(moon_ambiguity.message_zh)
        used_time = None
    else:
        hour, minute = birth_time.hour, birth_time.minute
        used_time = birth_time

    subject = _subject(
        name=subject_name,
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=hour,
        minute=minute,
        city=city_lookup,
        nation=nation,
        geonames_username=geonames_username,
    )

    context_xml = to_context(subject)
    if time_unknown:
        context_xml = _strip_houses_and_angles(context_xml)

    if moon_ambiguity:
        context_xml += (
            "\n<moon_ambiguity"
            f' sign_at_00="{moon_ambiguity.sign_at_start}"'
            f' sign_at_24="{moon_ambiguity.sign_at_end}"'
            " note=\"Birth time unknown; Moon changed signs that calendar day."
            " Discuss both possibilities; do not pick one.\" />\n"
        )

    svg = _svg_for_subject(subject)
    asc_sign = ""
    if not time_unknown and getattr(subject, "ascendant", None) is not None:
        asc_sign = subject.ascendant.sign

    return ChartResult(
        subject_name=subject_name,
        birth_date=birth_date,
        birth_time=used_time,
        time_unknown=time_unknown,
        city=city_input,
        nation=nation,
        mbti=mbti,
        context_xml=context_xml,
        svg=svg,
        moon_ambiguity=moon_ambiguity,
        preface_notes=notes,
        resolved_city=getattr(subject, "city", city_lookup),
        resolved_tz=getattr(subject, "tz_str", "") or "",
        sun_sign=subject.sun.sign,
        moon_sign=subject.moon.sign,
        asc_sign=asc_sign,
    )
