# History

Decision and spike log for **zodiacxMBTI**. Paper review sealed at **v1.4** (2026-07-21). After that, answers come from running code — no fourth round of plan polishing.

Source of truth for the sealed plan: [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md).

## Timeline

| When | What |
|---|---|
| 2026-07-21 | Plan sealed at v1.4 (moon sign-change; signal grading). Paper review ends. |
| 2026-07-21 | Repo bootstrap: `.gitignore`, MIT `LICENSE`, docs. |
| 2026-07-21 | Full spike path: `chart` / `interpret` / `tarot` / `app`, secrets example, GeoNames + DeepSeek local runs. |
| 2026-07-21 | UI: streaming LLM, summary card, country dropdown, CN chart expander, tarot 3D flip (LuciellaES CC0), exports. |
| 2026-07-21 | Prompt: psychological-astrology persona + anti-Barnum in `MAIN_SYSTEM`. |
| 2026-07-21 | Theme: dark starfield + vignette/grain; Instrument Serif / Space Grotesk / Noto Sans SC; glass summary. |
| 2026-07-21 | Chart: wheel-only dark SVG + CJK font injection (fix CN side-tables overlapped on mobile). |
| 2026-07-21 | Fix: stop global `span { font-family }` so expander `.arrow_` icons don’t collide with labels. |
| 2026-07-21 | Export: full-page HTML snapshot (chart + cards + report); keep lightweight text PDF. Print-from-HTML for visual PDF. |
| 2026-07-21 | Report craft: contradiction hooks in-body; compress main ~1000–1300 / tarot ~500–650; tarot closing = 三张牌共同指向 hammer. |
| 2026-07-21 | §6 延伸探索 restored as 3 titled short answers (not teaser CTAs); UI/HTML render as collapsed expanders/`<details>`. |
| 2026-07-22 | Visual system: `design_system.py` shared tokens; night-sky palette + Kaiti display; hero + coordinate strip; drop Google Fonts/grain; a11y (reduced-motion, focus, CTA contrast); tarot/chart `st.html`/`height="content"`; `tests/test_design_system.py`; Streamlit `toolbarMode=minimal`. |
| 2026-07-22 | Ship: Streamlit Community Cloud app live (`*.streamlit.app`); `prepare friend beta` removes mis-committed `.understand-anything` / `.workbuddy` / daily logs from git tracking + `.gitignore`. |
| 2026-07-22 | Fix: mobile expander `_arrow_right` overlap — hide Material toggle glyphs; §6 uses native HTML `<details>` (not `st.expander`). Causes: CJK font override on icon spans + China CDN flaky Material Symbols. Commit `15fe5c5`. |
| 2026-07-22 | Fix: Cloud empty birth date — tolerate `None` from date/time widgets; validate before build; coordinate strip shows `DATE REQUIRED` / `TIME REQUIRED`. Pin `streamlit==1.59.2`. Commit `aec3551`. |
| 2026-07-22 | Persona cards: full **192** pool in `persona_cards/persona_cards.json`; pct rule = `MBTI_midpoint / 12`; design doc `人设卡_设计稿.md` updated (seeds kept as examples). |
| 2026-07-22 | Question-section repair: if user filled「想问的事」but model skipped/short §4, call `generate_question_section` + `upsert_question_section`; show `_render_question_card`; tests in `tests/test_question_flow.py`. Commit `bcb0c66`. |
| 2026-07-23 | Docs: `architecture.md` / `agent.md` catch up on §4 repair, §6 `<details>`, persona-card side assets (offline, not in app). |
| 2026-07-23 | Persona card in-app: `persona_cards.py` lookup → result page after summary + HTML/PDF export; 12 zodiac masters + 192 JSON copy; MBTI unknown → hint. |
| 2026-07-24 | Fix: natal chart SVG no longer inside collapsed `st.expander` — Cloud first paint measured iframe height as 0px; chart now inline with responsive `height="content"`. |
| 2026-07-24 | Fix: mobile still hid chart (iframe `height="content"` → 0). Switch natal SVG to `st.html` page-DOM render with CSS `aspect-ratio`; drop `st.iframe`. |
| 2026-07-24 | Persona-card art switched to `personapicture/zodiac_tarot_masters/v1/`: 12 full 3:5 Art Nouveau tarot masters, six male / six female. Former `zodiac_masters/v1/` set archived; runtime and exports now use the tarot set without cropping. |
| 2026-07-27 | Docs map: add `DOCS.md`; sync README/SHIP/agent — no `memory.md` (use `history.md` / `agent.md` for durable context). |
| 2026-07-27 | UX five-fix (`log20260727.md`): natal chart via base64 `<img>` (DOMPurify was stripping raw SVG); 公历 date label; Shanxi/Shaanxi city hint; friendly API errors + tech expander; downloads in collapsed expander. |
| 2026-07-27 | Mentor triage batches A–C: empty date + MBTI sentinel defaults; dynamic CTA + privacy near submit; sun/combo hints; `usage_stats` SQLite (generation + §1–5 hit/miss); CN city map; question `text_area` up; persona PNG share. Commit `e09567f`. |
| 2026-07-27 | Aries ×16 `mbti_tarot_cards/aries/v1` wired; persona art via `st.image` + JPEG preview for HTML export (`a8b1bba`). |
| 2026-07-27 | Cloud operator panel: footer「运营统计」+ `STATS_PASSWORD` + JSON snapshot (`fcfbac4`). Docs: `log20260727_mentor.md`. |
| 2026-07-27 | Taurus ×16 `mbti_tarot_cards/taurus/v1` ready; same lookup path as Aries (no code change). |
| 2026-07-27 | Offline compositor shipped: `tools/build_cards.py` + `assets/cards/manifest.json` runtime lookup + Aries/Taurus/Gemini WebP batches (`67f123b`). |
| 2026-07-27 | Cancer ×16 WebP batch added to manifest/runtime (`b45265e`). |
| 2026-07-27 | Leo ×16 WebP batch added to manifest/runtime (`8800c10`). |
| 2026-07-28 | Virgo + Libra ×16 WebP batches added; docs synced to 112 shipped cards. |

## Watch list (not in spike)

- Chart art polish, conversational follow-ups, English UI (sealed plan)
- Classical interpretation rule packs (aryaminus/astro-style) after commercialization review
- Bloom-style scroll-video landing as a **separate** static page (not inside Streamlit)
- True server-side visual PDF (complex kerykeion SVG ≈ unsupported in fpdf2)

## Version notes (plan)

| Version | Delta |
|---|---|
| v1.2 | Optional tarot; half-day cap |
| v1.3 | Two-leg acceptance; disclaimer; secrets + spend cap; session_state for reruns |
| v1.4 | Moon day-boundary ambiguity; weak vs strong pull signals; freeze paper review |

## Locked product boundary

- Free, no promotion, no fees, no user accounts.
- Audience ≈ 10 Chinese-speaking friends, mobile link.
- Outside career C++ tooling track — amateur timebox only.

## Five-step review archive (summary)

### Kept

- Birth date / time / place;「不知道出生时间」
- MBTI dropdown (no quiz)
- Chart visualization via kerykeion
- LLM one-shot Chinese interpretation
- Optional tarot second step

### Deleted

- astro-seek scraping; GPT chart images; MBTI item bank; accounts/DB; custom React/Vercel frontend

### Simplified

- Streamlit single app; kerykeion only; GeoNames via kerykeion

## Acceptance & kill criteria

**Quantitative:** two weeks after share, LLM calls show spontaneous volume beyond first wave.

**Qualitative:** ask ~10 friends about reuse/forward. Strong signal = forward to strangers who then use.

**Stop if:** unfinished in two weekends; or no spontaneous reuse in two weeks.

## References

- Planning: zodiac-engine, kerykeion docs, AstroChart_Analysis, Aurora-MBTI, Astrologer-API
- Prompt craft: [astrologyprompt.com](https://astrologyprompt.com) (external calc + ground-truth-only paradigm)
- Tarot art: LuciellaES CC0 RWS
- UI mood (not cloned into Streamlit): local `bloom.html` glass / dark reference
