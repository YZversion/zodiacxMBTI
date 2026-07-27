from __future__ import annotations

import unittest
from pathlib import Path

from persona_cards import (
    FOOTNOTE,
    MASTERS_DIR,
    MBTI_TAROT_ROOT,
    PERSONA_CARD_CSS,
    build_persona_card_html,
    build_persona_missing_html,
    card_id,
    lookup_persona_card,
    master_image_path,
    normalize_sun_en,
    persona_art_path,
    unique_mbti_card_path,
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
            self.assertEqual(path.parent, MASTERS_DIR)
            self.assertIn(
                path.name,
                {
                    "01_aries_male.png",
                    "02_taurus_female.png",
                    "03_gemini_male.png",
                    "04_cancer_female.png",
                    "05_leo_male.png",
                    "06_virgo_female.png",
                    "07_libra_male.png",
                    "08_scorpio_female.png",
                    "09_sagittarius_female.png",
                    "10_capricorn_male.png",
                    "11_aquarius_female.png",
                    "12_pisces_male.png",
                },
            )

    def test_tarot_master_art_is_shown_without_cropping(self) -> None:
        self.assertIn("aspect-ratio: 3 / 5", PERSONA_CARD_CSS)
        self.assertIn("object-fit: contain", PERSONA_CARD_CSS)
        self.assertNotIn("max-height: 320px", PERSONA_CARD_CSS)
        self.assertNotIn("max-height: 280px", PERSONA_CARD_CSS)

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

    def test_html_embeds_new_tarot_master(self) -> None:
        card = lookup_persona_card(mbti="INFP", sun_sign="Ari")
        self.assertIsNotNone(card)
        assert card is not None
        fragment = build_persona_card_html(card)
        self.assertIn('class="zx-persona-art"', fragment)
        self.assertIn("data:image/", fragment)
        self.assertIn("base64,", fragment)

    def test_aries_prefers_unique_mbti_card(self) -> None:
        unique = unique_mbti_card_path(mbti="INTJ", sun_en="Aries")
        self.assertIsNotNone(unique)
        assert unique is not None
        self.assertEqual(unique.parent, MBTI_TAROT_ROOT / "aries" / "v1")
        self.assertIn("INTJ_Aries", unique.name)
        art = persona_art_path(mbti="INTJ", sun_en="Aries")
        self.assertEqual(art, unique)

    def test_non_aries_falls_back_to_shared_master(self) -> None:
        self.assertIsNone(unique_mbti_card_path(mbti="INTJ", sun_en="Scorpio"))
        art = persona_art_path(mbti="INTJ", sun_en="Scorpio")
        master = master_image_path("Scorpio")
        self.assertEqual(art, master)
        self.assertEqual(art.parent if art else None, MASTERS_DIR)

    def test_aries_set_has_all_16_mbti(self) -> None:
        types = [
            "ISTJ",
            "ISFJ",
            "INFJ",
            "INTJ",
            "ISTP",
            "ISFP",
            "INFP",
            "INTP",
            "ESTP",
            "ESFP",
            "ENFP",
            "ENTP",
            "ESTJ",
            "ESFJ",
            "ENFJ",
            "ENTJ",
        ]
        for mbti in types:
            path = unique_mbti_card_path(mbti=mbti, sun_en="Aries")
            self.assertIsNotNone(path, mbti)
            assert path is not None
            self.assertTrue(path.is_file(), path)

    def test_missing_hint(self) -> None:
        html = build_persona_missing_html()
        self.assertIn("zx-persona-missing", html)
        self.assertIn("MBTI", html)


if __name__ == "__main__":
    unittest.main()
