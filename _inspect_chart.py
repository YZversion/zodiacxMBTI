from datetime import date, time
import re
from chart import build_chart
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer

c = build_chart(
    birth_date=date(2001, 4, 19),
    birth_time=time(6, 0),
    time_unknown=False,
    city="Shenzhen",
    nation="CN",
    mbti="INTJ",
    geonames_username="badwomanbzzb",
)
open("_chart_preview.svg", "w", encoding="utf-8").write(c.svg)
print("svg len", len(c.svg))
texts = re.findall(r"<text[^>]*>([^<]+)</text>", c.svg)
print("n_texts", len(texts))
print("sample", texts[:30])
fonts = set(re.findall(r"font-family:([^;\"']+)", c.svg))
sizes = set(re.findall(r"font-size:([^;\"']+)", c.svg))
print("fonts", fonts)
print("sizes", sizes)

# Compare EN vs CN density
subject = AstrologicalSubjectFactory.from_birth_data(
    "T", 2001, 4, 19, 6, 0, city="Shenzhen", nation="CN",
    geonames_username="badwomanbzzb", online=True, suppress_geonames_warning=True,
)
data = ChartDataFactory.create_natal_chart_data(subject)
for lang in ("EN", "CN"):
    svg = ChartDrawer(chart_data=data, theme="dark", chart_language=lang, custom_title="本命盘").generate_svg_string()
    t = re.findall(r"<text[^>]*>([^<]+)</text>", svg)
    print(lang, "texts", len(t), "avg_len", round(sum(len(x) for x in t)/max(len(t),1), 2))
