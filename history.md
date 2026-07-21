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
| 2026-07-21 | Report quality (canary feedback): optional「想问的事」; five-section MAIN_SYSTEM (金钱与事业 + 纠结专节 + 钩子句); tarot Q prefill. |

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
