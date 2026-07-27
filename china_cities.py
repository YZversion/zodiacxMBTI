"""Chinese city name → GeoNames English lookup (CN only). Exact match; no fuzzy guess."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "china_cities.json"


@lru_cache(maxsize=1)
def _load_map() -> dict[str, str]:
    if not DATA_PATH.is_file():
        return {}
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for zh, en in (raw or {}).items():
        key = str(zh).strip()
        val = str(en).strip()
        if key and val:
            out[key] = val
    return out


def resolve_china_city(city: str) -> Optional[str]:
    """Return English GeoNames city if exact CN map hit; else None.

    Exact match first; only strip trailing「市」(prefecture-level shorthand).
    Do NOT strip 县/区 — e.g. 西安区 must not become Xi'an (Shaanxi).
    Ambiguous / unmapped input falls through to GeoNames as-is.
    """
    raw = (city or "").strip()
    if not raw:
        return None
    mapping = _load_map()
    if raw in mapping:
        return mapping[raw]
    # Only「市」: 上海市 → 上海. Never 区/县 (wrong-city risk).
    if raw.endswith("市") and len(raw) > 1:
        base = raw[:-1]
        if base in mapping:
            return mapping[base]
    return None


def maybe_resolve_city(city: str, nation: str) -> str:
    """For CN, substitute mapped English name when known; otherwise return original."""
    text = (city or "").strip()
    if not text:
        return text
    if (nation or "").strip().upper() != "CN":
        return text
    mapped = resolve_china_city(text)
    return mapped if mapped else text
