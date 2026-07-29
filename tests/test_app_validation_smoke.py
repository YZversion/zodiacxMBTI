"""AppTest edge cases for validation / CTA."""
from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class AppValidationSmoke(unittest.TestCase):
    def test_empty_city_blocked_after_date_and_mbti(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
        app.date_input[0].set_value(date(1995, 6, 15))
        # select MBTI past placeholder: index 1 = INTJ
        app.selectbox[1].set_value("INTJ")
        gen = [b for b in app.button if b.key == "generate_report"]
        gen[0].click()
        app.run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("城市" in e.value or "拼音" in e.value or "Shanghai" in e.value for e in app.error) or len(app.error) >= 1)

    def test_button_label_uses_greek_sun_without_mbti(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
        app.date_input[0].set_value(date(1995, 11, 1))
        app.selectbox[1].set_value("INTJ")
        app.run(timeout=20)
        gen = [b for b in app.button if b.key == "generate_report"]
        self.assertTrue(gen)
        self.assertEqual(gen[0].label, "解读 σκορπίος")
        self.assertNotIn("INTJ", gen[0].label)
        self.assertNotIn("天蝎", gen[0].label)


if __name__ == "__main__":
    unittest.main()
