from __future__ import annotations

import unittest
from pathlib import Path

from persona_cards import (
    FOOTNOTE,
    build_persona_card_html,
    build_persona_missing_html,
    card_id,
    lookup_persona_card,
    master_image_path,
    normalize_sun_en,
)


ROOT = Path(__file__).resolve().parents[1]


class PersonaCardTests(unittest.TestCase):
    def test_normalize_kerykeion_abbr(self) -> None:
        self.assertEqual(normalize_sun_en("Ari"), "Aries")
        self.assertEqual(normalize_sun_en("Pis"), "Pisces")
        self.assertEqual(normalize_sun_en("Aries"), "Aries")

    def test_lookup_unique_card(self) -> None:
        card = lookup_persona_card(mbti="INFP", sun_sign="Ari")
        self.assertIsNotNone(card)
        assert card is not None
        self.assertEqual(card.id, "INFP_Aries")
        self.assertEqual(card.mbti, "INFP")
        self.assertEqual(card.sun_en, "Aries")
        self.assertTrue(card.nickname)
        self.assertIn("÷12", card.pct_line)

    def test_unknown_mbti_skips_card(self) -> None:
        self.assertIsNone(lookup_persona_card(mbti=None, sun_sign="Ari"))
        self.assertIsNone(lookup_persona_card(mbti="不确定", sun_sign="Ari"))

    def test_pool_has_192_and_master_files(self) -> None:
        from persona_cards import _load_cards

        cards = _load_cards()
        self.assertEqual(len(cards), 192)
        self.assertEqual(len({c.nickname for c in cards.values()}), 192)
        for sun in (
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ):
            path = master_image_path(sun)
            self.assertIsNotNone(path, sun)
            assert path is not None
            self.assertTrue(path.is_file(), path)

    def test_html_escapes_and_includes_fields(self) -> None:
        card = lookup_persona_card(mbti="INTJ", sun_sign="Sco")
        self.assertIsNotNone(card)
        assert card is not None
        fragment = build_persona_card_html(card, include_image=False)
        self.assertNotIn("<!DOCTYPE html>", fragment)
        self.assertIn("zx-persona-card", fragment)
        self.assertIn(card.nickname, fragment)
        self.assertIn(card.definition, fragment)
        self.assertIn(FOOTNOTE, fragment)
        self.assertIn(card_id("INTJ", "Scorpio"), card.id)

    def test_missing_hint(self) -> None:
        html = build_persona_missing_html()
        self.assertIn("zx-persona-missing", html)
        self.assertIn("MBTI", html)


if __name__ == "__main__":
    unittest.main()
