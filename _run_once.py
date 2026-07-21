from datetime import date, time
from pathlib import Path

import tomllib

from chart import build_chart
from interpret import generate_main_report

secrets = tomllib.loads(Path(".streamlit/secrets.toml").read_text(encoding="utf-8"))

print("Building chart for 2001-04-19 Shenzhen INTJ ...")
chart = build_chart(
    birth_date=date(2001, 4, 19),
    birth_time=time(12, 0),
    time_unknown=True,  # no birth time given
    city="Shenzhen",
    nation="CN",
    mbti="INTJ",
    geonames_username=secrets.get("GEONAMES_USERNAME"),
)
print("place:", chart.resolved_city, chart.resolved_tz)
print("notes:", chart.preface_notes)
print("moon_ambiguity:", chart.moon_ambiguity)
print("Calling DeepSeek ...")
report = generate_main_report(
    chart,
    api_key=secrets["OPENAI_API_KEY"],
    model=secrets.get("OPENAI_MODEL", "deepseek-chat"),
    base_url=secrets.get("OPENAI_BASE_URL") or None,
)
print("=" * 60)
print(report)
print("=" * 60)
print("DONE chars=", len(report), "svg=", len(chart.svg))
