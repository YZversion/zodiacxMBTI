# MBTI × Zodiac Tarot Card Generation SOP

Use this workflow for every 16-card zodiac set.

## 1. Lock the source of truth

- Use the matching image in `personapicture/zodiac_tarot_masters/v1/` as a **style and layout reference only**.
- Keep the nickname and personality idea from the supplied persona prompt data.
- Do not copy the master character's face, pose, clothing, or silhouette.

## 2. Build one prompt per card

- Use one built-in ImageGen call for each distinct card.
- Keep the shared 3:5 full-bleed frame, stained-glass language, cel shading, crisp ink, aged mosaic texture, and zodiac-specific halo.
- Make the subject, pose, clothing or anatomy, props, scene, and primary palette different for every MBTI.
- Replace writing-dependent concepts with blank paper, non-linguistic geometry, gems, mechanisms, or abstract light.
- Repeat the no-text and full-frame constraints in every prompt.

## 3. Generate in small batches

- Start with a mixed four-card pilot that covers the riskiest subject types.
- Generate later cards in groups of four.
- Copy only accepted results from the ImageGen default directory into the project.
- Preserve accepted cards; regenerate only the failed card with one targeted correction.

## 4. Visual quality gate

Check every card for:

- complete ornate border and full-bleed artwork;
- no bottom whitespace, title strip, caption, signature, watermark, or pseudo-writing;
- complete main subject with valid anatomy;
- correct zodiac symbols and no symbols inherited from another zodiac;
- clearly different composition and palette from the rest of the set.

For non-humanoid cards, also require a genuinely non-human silhouette and reject accidental humanoids, animal-eared people, or cropped legs, horns, wings, and tails.

## 5. Normalize and deliver

- Normalize accepted cards without cropping to `972 × 1620` PNG.
- Use `NN_MBTI_Sign_male|female|creature.png`.
- Generate a 4 × 4 `contact_sheet.png`.
- Add a set README with the manifest, reference master, prompt framework, type split, and visual concepts.
- Validate file count, unique MBTI coverage, PNG integrity, dimensions, naming, and runtime lookup before handoff.

## Runtime wiring (app)

- Lookup: `persona_cards.unique_mbti_card_path(mbti, sun_en)` → `personapicture/mbti_tarot_cards/{sign}/v1/*_{MBTI}_{Sun}_*.png`
- **Shipped:** `aries/v1` and `taurus/v1` (16 files each). Other signs fall back to `zodiac_tarot_masters/v1/` until their set lands.
- UI: result page uses `st.image` on the PNG path (not multi-MB base64 inside `st.html`).

