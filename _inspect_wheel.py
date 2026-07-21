from datetime import date
import re
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer

subject = AstrologicalSubjectFactory.from_birth_data(
    "本命", 2001, 4, 19, 6, 0, city="Shenzhen", nation="CN",
    geonames_username="badwomanbzzb", online=True, suppress_geonames_warning=True,
)
data = ChartDataFactory.create_natal_chart_data(subject)
drawer = ChartDrawer(
    chart_data=data,
    theme="dark",
    chart_language="CN",
    custom_title="本命盘",
    show_house_position_comparison=False,
    show_cusp_position_comparison=False,
)
full = drawer.generate_svg_string()
wheel = drawer.generate_wheel_only_svg_string()
print("full", len(full), "wheel", len(wheel))
print("full texts", len(re.findall(r"<text", full)), "wheel texts", len(re.findall(r"<text", wheel)))
# peek first 500 chars of svg tag
m = re.search(r"<svg[^>]*>", wheel)
print("wheel svg tag", m.group(0)[:300] if m else None)
open("_wheel.svg", "w", encoding="utf-8").write(wheel)
