# Aries × 16 MBTI Tarot Cards — v1

This directory contains the first complete Aries MBTI card set.

- Reference master: `personapicture/zodiac_tarot_masters/v1/01_aries_male.png`
- Generation method: built-in ImageGen with the reference master supplied as a style/layout reference
- Format: vertical 3:5 full-bleed tarot card
- Final card dimensions: 972 × 1620 px
- Gender split: 8 male / 8 female
- Text policy: no title bar, caption, letters, numbers, signature, watermark, or pseudo-writing

## Card manifest

| No. | File | MBTI | Nickname | Gender | Visual concept |
| ---: | --- | --- | --- | --- | --- |
| 01 | `01_ISTJ_Aries_male.png` | ISTJ | 规矩火药桶 | Male | A strict symmetrical rule array suppressing an imminent eruption |
| 02 | `02_ISFJ_Aries_female.png` | ISFJ | 暴躁小棉袄 | Female | A gentle caretaker surrounded by quietly boiling fire |
| 03 | `03_INFJ_Aries_male.png` | INFJ | 温柔炮仗 | Male | A calm counselor before a volcano at its breaking point |
| 04 | `04_INTJ_Aries_female.png` | INTJ | 闪电军师 | Female | A fast strategist commanding layered fire projections |
| 05 | `05_ISTP_Aries_male.png` | ISTP | 沉默莽夫 | Male | A silent flame mechanic beside an unrepaired bond |
| 06 | `06_ISFP_Aries_female.png` | ISFP | 佛系斗士 | Female | A relaxed guardian instantly raising a protective fire wall |
| 07 | `07_INFP_Aries_male.png` | INFP | 热血小哭包 | Male | Brave anger softening into warm sparks and tears |
| 08 | `08_INTP_Aries_female.png` | INTP | 理论敢死队 | Female | A scholar leaping into the danger she just calculated |
| 09 | `09_ESTP_Aries_male.png` | ESTP | 人形加速器 | Male | A full-speed runner leaving a blazing afterimage |
| 10 | `10_ESFP_Aries_female.png` | ESFP | 即兴纵火犯 | Female | A coral-and-magenta festival fire dancer |
| 11 | `11_ENFP_Aries_male.png` | ENFP | 三秒热心肠 | Male | An emerald messenger overloaded with blank promise scrolls |
| 12 | `12_ENTP_Aries_female.png` | ENTP | 杠精突击手 | Female | A violet-and-orange debate mage breaking abstract arguments |
| 13 | `13_ESTJ_Aries_male.png` | ESTJ | 铁腕急先锋 | Male | A crimson frontline commander with a blank banner and map |
| 14 | `14_ESFJ_Aries_female.png` | ESFJ | 热心纠察队 | Female | A rose-and-teal warden offering protective flame charms |
| 15 | `15_ENFJ_Aries_male.png` | ENFJ | 铁血知心人 | Male | An indigo guardian diving with a braided fire rescue rope |
| 16 | `16_ENTJ_Aries_female.png` | ENTJ | 先斩后奏王 | Female | A steel-blue and scarlet sovereign carrying revised blank plans |

## Shared prompt framework

Every card prompt applies the following invariant:

> Create one original vertical 3:5 full-bleed Aries × MBTI tarot character card. Use the Aries master only as a strict reference for its bone-ivory and antique-gold Art Nouveau frame, cathedral stained-glass rose window, ram-horn halo, crisp ink, flat cel-shaded anime rendering, and aged mosaic/crackle texture. Keep one complete adult character and all ornate borders fully visible. Fill the entire card with artwork. Do not copy the master character's face, pose, outfit, or silhouette.

Every prompt also includes this avoid list:

> No words, letters, numbers, initials, MBTI labels, zodiac names, signatures, watermarks, logos, gibberish, pseudo-writing, title strip, bottom whitespace, caption, plaque, cropped limbs, duplicate body parts, malformed hands, extra people, photorealism, 3D rendering, watercolor, or chibi styling.

The per-card subject, action, clothing, palette, and Aries symbolism are defined by the manifest above and were supplied separately for each generation call.
