# Zodiac master artworks v1

Generated with the built-in `imagegen` workflow on 2026-07-23.

## Purpose

These 12 images are reusable zodiac hero illustrations for the upper portion of
the 192 MBTI × zodiac persona cards. Chinese card copy, MBTI, zodiac name,
rarity, and disclaimer should be rendered separately by the deterministic card
layout. Do not ask an image model to draw those fields.

All source images are 1086 × 1448 (3:4). Detailed illustration occupies roughly
the upper 65%; the lower area fades into the shared dark background for copy.

## Shared art direction

- Deep navy celestial background: `#07101d` / `#0b1626`
- Ivory constellation nodes: `#e7ddc9`
- Copper-gold line work: `#a76d46`
- One elegant androgynous adult celestial avatar
- Refined constellation-map and coordinate geometry
- Dark editorial luxury; original visual identity; not anime or photorealistic
- No text, letters, numbers, calligraphy, signatures, watermark, logo, UI,
  border, or card frame
- The approved Aries image was used as the strict visual reference for the
  remaining 11 images

## Asset map

| File | Zodiac | Distinguishing motif | Accent palette |
|---|---|---|---|
| `01_aries.png` | Aries / 白羊座 | Ram-horn constellation halo | Molten coral red and orange |
| `02_taurus.png` | Taurus / 金牛座 | Broad bull-horn halo, gemstones | Deep emerald and antique gold |
| `03_gemini.png` | Gemini / 双子座 | Mirrored after-image, twin arcs | Silver and cyan |
| `04_cancer.png` | Cancer / 巨蟹座 | Protective crab halo, warm heart light | Moonlit silver and tide blue |
| `05_leo.png` | Leo / 狮子座 | Celestial lion profile and mane | Radiant gold and warm amber |
| `06_virgo.png` | Virgo / 处女座 | Wheat-and-veil halo | Pale jade and porcelain white |
| `07_libra.png` | Libra / 天秤座 | Symmetric suspended balance | Rose gold and ivory |
| `08_scorpio.png` | Scorpio / 天蝎座 | Curved scorpion and poised stinger | Deep crimson and near-black violet |
| `09_sagittarius.png` | Sagittarius / 射手座 | Drawn constellation bow and arrow | Amber and violet horizon fire |
| `10_capricorn.png` | Capricorn / 摩羯座 | Goat horns, mountain, sea-tail arc | Slate blue and weathered bronze |
| `11_aquarius.png` | Aquarius / 水瓶座 | Vessel pouring constellation light | Electric blue and violet |
| `12_pisces.png` | Pisces / 双鱼座 | Two orbiting luminous fish | Iridescent teal and lavender |

## Reusable prompt structure

```text
Use case: stylized-concept
Asset type: reusable zodiac hero illustration for the upper portion of a 3:4
Chinese personality card

Input image: the approved Aries master is a strict visual reference for
composition, rendering, avatar scale, dark navy backdrop, copper-gold
constellation filaments, and lower text-safe fade. Create a new zodiac companion
artwork; do not edit the reference.

Subject: one elegant androgynous adult celestial avatar, three-quarter body.
Replace the zodiac halo, pose cue, atmosphere, and restrained accent palette
with the values in the asset map.

Composition: vertical 3:4. Keep detailed artwork in the upper 60–65%. Preserve a
clean near-black navy lower 35% for later Chinese typography. Use generous safe
margins and keep the zodiac motif fully within frame.

Constraints: preserve the approved master style and dark luxury mood.
Illustration only. No text, letters, words, numbers, calligraphy, zodiac name,
signatures, watermark, logo, UI, border, card frame, artist imitation, extra
characters, anime styling, photorealism, or clutter in the lower text-safe
region.
```

`contact_sheet.png` is a QA-only overview and is not a production card asset.
