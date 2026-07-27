from __future__ import annotations

import tomllib
import unittest
import inspect
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest

from app import THEME_CSS, _fingerprint, _render_svg
from design_system import COLORS, css_variables
from report_export import build_report_html
from tarot import DrawnCard
from tarot_ui import build_flip_html


ROOT = Path(__file__).resolve().parents[1]


class DesignSystemTests(unittest.TestCase):
    def test_submitted_question_is_rendered_visibly_and_escaped(self) -> None:
        code = """
from app import _render_question_card

_render_question_card('要不要生孩子哈哈哈 <script>alert(1)</script>')
"""
        app = AppTest.from_string(code).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.get("html")), 1)
        body = app.get("html")[0].proto.body
        self.assertIn("本次问题", body)
        self.assertIn("要不要生孩子哈哈哈", body)
        self.assertNotIn("<script>", body)

    def test_empty_date_is_rendered_and_fingerprinted_safely(self) -> None:
        code = """
from app import _render_coordinate_strip

_render_coordinate_strip(
    birth_date=None,
    birth_time=None,
    time_unknown=False,
    city="",
    mbti="不确定",
)
"""
        app = AppTest.from_string(code).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.get("html")), 1)
        self.assertIn("DATE REQUIRED", app.get("html")[0].proto.body)
        self.assertEqual(
            _fingerprint(None, None, False, "", "CN", "不确定")[0],
            None,
        )

    def test_submit_with_empty_date_shows_validation_instead_of_crashing(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
        app.date_input[0].set_value(None)
        app.button[0].click()
        app.run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([item.value for item in app.error], ["请选择出生日期。"])

    def test_theme_has_accessibility_guards_and_no_remote_fonts(self) -> None:
        self.assertIn("@media (prefers-reduced-motion: reduce)", THEME_CSS)
        self.assertIn("button:focus-visible", THEME_CSS)
        self.assertIn("color: var(--zx-cta-text)", THEME_CSS)
        self.assertNotIn("fonts.googleapis.com", THEME_CSS)
        self.assertNotIn("zx-drift-grain", THEME_CSS)

    def test_streamlit_theme_matches_shared_tokens(self) -> None:
        config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text("utf-8"))
        self.assertEqual(config["theme"]["primaryColor"], COLORS["cta"])
        self.assertEqual(config["theme"]["backgroundColor"], COLORS["bg"])
        self.assertEqual(config["theme"]["secondaryBackgroundColor"], COLORS["surface"])
        self.assertEqual(config["theme"]["textColor"], COLORS["text"])
        self.assertEqual(config["theme"]["headingFont"], "serif")
        self.assertEqual(config["client"]["toolbarMode"], "minimal")

    def test_tarot_fragment_is_inline_responsive_and_reduced_motion_safe(self) -> None:
        cards = [
            DrawnCard("大阿卡纳·愚者", "过去", False),
            DrawnCard("大阿卡纳·魔术师", "现在", True),
            DrawnCard("大阿卡纳·女祭司", "未来", False),
        ]
        fragment = build_flip_html(cards)
        self.assertNotIn("<!DOCTYPE html>", fragment)
        self.assertNotIn("<body", fragment)
        self.assertIn("zx-tarot-stage", fragment)
        self.assertIn("grid-template-columns", fragment)
        self.assertIn("@media (prefers-reduced-motion: reduce)", fragment)
        self.assertIn(css_variables().splitlines()[0], fragment)

    def test_export_uses_shared_visual_tokens(self) -> None:
        chart = SimpleNamespace(
            sun_sign="Ari",
            moon_sign="Tau",
            asc_sign="Gem",
            moon_ambiguity=None,
            mbti="INTJ",
            time_unknown=False,
            resolved_city="Shanghai",
            city="Shanghai",
            nation="CN",
            resolved_tz="Asia/Shanghai",
            birth_date=date(1995, 1, 1),
            birth_time=SimpleNamespace(strftime=lambda _fmt: "12:00"),
            preface_notes=[],
            svg='<svg viewBox="0 0 10 10"></svg>',
        )
        page = build_report_html(chart=chart, report_text="## 1. 核心性格画像\n测试")
        self.assertIn(f"--zx-bg: {COLORS['bg']}", page)
        self.assertIn("var(--zx-coordinate)", page)
        self.assertNotIn("#c9a46c", page.lower())
        self.assertIn("zx-persona-card", page)
        self.assertIn("你的隐藏人格", page)

    def test_chart_and_tarot_render_without_fixed_height_iframes(self) -> None:
        code = """
from app import _inject_theme, _render_svg, _render_tarot_cards
from tarot import DrawnCard

_inject_theme()
_render_svg('<svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" /></svg>')
_render_tarot_cards([
    DrawnCard("大阿卡纳·愚者", "过去", False),
    DrawnCard("大阿卡纳·魔术师", "现在", True),
    DrawnCard("大阿卡纳·女祭司", "未来", False),
])
"""
        app = AppTest.from_string(code).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        # Theme via markdown; natal chart as base64 <img> (DOMPurify strips raw SVG)
        self.assertEqual(len(app.markdown), 1)
        self.assertIn("<style>", app.markdown[0].value)
        self.assertIn("stAppViewContainer", app.markdown[0].value)
        self.assertIn("zx-natal-chart", app.markdown[0].value)
        self.assertEqual(len(app.get("iframe")), 0)
        html_bodies = [item.proto.body for item in app.get("html")]
        self.assertTrue(any("zx-natal-chart" in body for body in html_bodies))
        self.assertTrue(
            any("data:image/svg+xml;base64," in body for body in html_bodies)
        )
        self.assertTrue(any("<img" in body for body in html_bodies))
        source = inspect.getsource(_render_svg)
        self.assertIn("st.html", source)
        self.assertIn("base64", source)
        self.assertNotIn("st.iframe(", source)


if __name__ == "__main__":
    unittest.main()
