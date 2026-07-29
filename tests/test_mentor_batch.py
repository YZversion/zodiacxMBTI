"""Tests for Batch A/C helpers: sun preview, CN cities, section split, persona PNG."""

from __future__ import annotations

import unittest
from datetime import date

from china_cities import maybe_resolve_city, resolve_china_city
from persona_cards import build_persona_share_png, lookup_persona_card
from report_export import split_numbered_sections
from sun_preview import approximate_sun_sign_greek, approximate_sun_sign_zh


class SunPreviewTests(unittest.TestCase):
    def test_known_mid_sign(self) -> None:
        sign, near = approximate_sun_sign_zh(date(1995, 5, 1))
        self.assertEqual(sign, "金牛")
        self.assertFalse(near)

    def test_cusp_flag(self) -> None:
        sign, near = approximate_sun_sign_zh(date(1995, 4, 20))
        self.assertEqual(sign, "金牛")
        self.assertTrue(near)

    def test_capricorn_january(self) -> None:
        sign, _near = approximate_sun_sign_zh(date(1995, 1, 10))
        self.assertEqual(sign, "摩羯")

    def test_greek_cta_names(self) -> None:
        self.assertEqual(approximate_sun_sign_greek(date(2001, 4, 19))[0], "κριός")
        self.assertEqual(approximate_sun_sign_greek(date(1995, 7, 1))[0], "καρκίνος")
        self.assertEqual(approximate_sun_sign_greek(date(1995, 11, 1))[0], "σκορπίος")


class ChinaCityTests(unittest.TestCase):
    def test_exact_and_suffix(self) -> None:
        self.assertEqual(resolve_china_city("西安"), "Xi'an")
        self.assertEqual(resolve_china_city("上海市"), "Shanghai")
        self.assertIsNone(resolve_china_city("不存在的城"))

    def test_district_suffix_not_stripped(self) -> None:
        # 西安区 must NOT become Xi'an (Shaanxi) — wrong-city risk
        self.assertIsNone(resolve_china_city("西安区"))
        self.assertIsNone(resolve_china_city("黄山区"))

    def test_apostrophe_romanization(self) -> None:
        self.assertEqual(resolve_china_city("六安"), "Lu'an")
        self.assertEqual(resolve_china_city("淮安"), "Huai'an")

    def test_only_cn_nation(self) -> None:
        self.assertEqual(maybe_resolve_city("北京", "CN"), "Beijing")
        self.assertEqual(maybe_resolve_city("北京", "US"), "北京")


class SectionSplitTests(unittest.TestCase):
    def test_split_1_to_5(self) -> None:
        report = (
            "## 1. 核心性格画像\n甲\n\n"
            "## 2. 关系模式\n乙\n\n"
            "## 3. 金钱与工作\n丙\n\n"
            "## 4. 针对你的问题\n丁\n\n"
            "## 5. 一句话建议\n戊"
        )
        parts = split_numbered_sections(report)
        nums = [n for n, _, _ in parts]
        self.assertEqual(nums, [1, 2, 3, 4, 5])
        self.assertIn("甲", parts[0][2])


class PersonaPngTests(unittest.TestCase):
    def test_png_bytes(self) -> None:
        card = lookup_persona_card(mbti="INTJ", sun_sign="Sco")
        self.assertIsNotNone(card)
        assert card is not None
        png = build_persona_share_png(card)
        self.assertTrue(png.startswith(b"\x89PNG"))


if __name__ == "__main__":
    unittest.main()
