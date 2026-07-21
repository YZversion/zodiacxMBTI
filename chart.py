"""Natal chart computation via kerykeion."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import Optional

from kerykeion import AstrologicalSubjectFactory, ChartDataFactory, to_context
from kerykeion.charts.chart_drawer import ChartDrawer

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
    "请用拼音或英文城市名（如 Shanghai、Beijing），"
    "若解析失败可改输入附近更大的城市，误差可忽略。"
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


def _svg_for_subject(subject) -> str:
    chart_data = ChartDataFactory.create_natal_chart_data(subject)
    return ChartDrawer(chart_data=chart_data).generate_svg_string()


def build_chart(
    *,
    birth_date: date,
    birth_time: Optional[time],
    time_unknown: bool,
    city: str,
    nation: str,
    mbti: Optional[str],
    geonames_username: Optional[str] = None,
    subject_name: str = "You",
) -> ChartResult:
    if not city or not city.strip():
        raise PlaceLookupError(PLACE_HINT)

    nation = (nation or "CN").strip().upper() or "CN"
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
            city=city,
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
        city=city,
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

    return ChartResult(
        subject_name=subject_name,
        birth_date=birth_date,
        birth_time=used_time,
        time_unknown=time_unknown,
        city=city.strip(),
        nation=nation,
        mbti=mbti,
        context_xml=context_xml,
        svg=svg,
        moon_ambiguity=moon_ambiguity,
        preface_notes=notes,
        resolved_city=getattr(subject, "city", city),
        resolved_tz=getattr(subject, "tz_str", "") or "",
    )
