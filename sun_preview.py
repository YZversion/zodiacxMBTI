"""Approximate tropical sun sign from calendar date (preview only; not kerykeion)."""

from __future__ import annotations

from datetime import date


def approximate_sun_sign_zh(birth_date: date) -> tuple[str, bool]:
    """Return (中文座名, near_cusp).

    near_cusp True when within 1 calendar day of a sign boundary (trust warning).
    Preview may disagree with kerykeion on cusp days — label as approximate in UI.
    """
    sign = _resolve_sign(birth_date)
    near = _near_cusp(birth_date)
    return sign, near


def _resolve_sign(birth_date: date) -> str:
    md = (birth_date.month, birth_date.day)
    ranges = [
        ((3, 21), (4, 19), "白羊"),
        ((4, 20), (5, 20), "金牛"),
        ((5, 21), (6, 21), "双子"),
        ((6, 22), (7, 22), "巨蟹"),
        ((7, 23), (8, 22), "狮子"),
        ((8, 23), (9, 22), "处女"),
        ((9, 23), (10, 23), "天秤"),
        ((10, 24), (11, 22), "天蝎"),
        ((11, 23), (12, 21), "射手"),
        ((12, 22), (12, 31), "摩羯"),
        ((1, 1), (1, 19), "摩羯"),
        ((1, 20), (2, 18), "水瓶"),
        ((2, 19), (3, 20), "双鱼"),
    ]
    for start, end, name in ranges:
        if start <= md <= end:
            return name
    return "摩羯"


def _near_cusp(birth_date: date) -> bool:
    boundaries = [
        (3, 21),
        (4, 20),
        (5, 21),
        (6, 22),
        (7, 23),
        (8, 23),
        (9, 23),
        (10, 24),
        (11, 23),
        (12, 22),
        (1, 20),
        (2, 19),
    ]
    for m, d in boundaries:
        try:
            boundary = date(birth_date.year, m, d)
        except ValueError:
            continue
        if abs((birth_date - boundary).days) <= 1:
            return True
        try:
            prev = date(birth_date.year - 1, m, d)
            if abs((birth_date - prev).days) <= 1:
                return True
        except ValueError:
            pass
    return False
