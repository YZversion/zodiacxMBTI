# History

Decision and spike log for **zodiacxMBTI**. Paper review sealed at **v1.4** (2026-07-21). After that, answers come from running code — no fourth round of plan polishing.

Source of truth for the sealed plan: [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md).

## Timeline

| When | What |
|---|---|
| 2026-07-21 | Plan sealed at v1.4 (moon sign-change handling; friend-sample bias / signal grading). Paper review ends. |
| 2026-07-21 | Repo bootstrap: `.gitignore`, MIT `LICENSE`, `README.md`, `agent.md`, `architecture.md`, `history.md`. Application code not started. |
| 2026-07-21 | Implemented full spike path: `chart.py` / `interpret.py` / `tarot.py` / `app.py`, `requirements.txt`, Streamlit secrets example. Session-state cache + unknown-time / moon-ambiguity / optional tarot. |
| 2026-07-21 | UI polish: streaming LLM, summary card, CN chart expander, country dropdown, tarot flip stage (LuciellaES CC0 assets) + beige starfield background. |
| 2026-07-21 | Prompt: psychological-astrology persona + anti-Barnum rule in `MAIN_SYSTEM` (astrologyprompt.com-aligned). Classical rule-bank deferred to watch list. |

## Watch list (not in spike)

- Chart art polish, conversational follow-ups, English UI (from sealed plan)
- Inject classical interpretation rule packs (e.g. aryaminus/astro style) so the model grounds aspect meanings in an explicit rule set rather than latent memory — only after commercialization review

## Version notes (plan)

| Version | Delta |
|---|---|
| v1.2 | Optional tarot block at bottom of report (friend-requested); half-day cap; cut first if weekend two slips |
| v1.3 | Two-leg acceptance (quantitative API delta + qualitative friend interviews); disclaimer; secrets + spend cap; Streamlit rerun/`session_state` pitfall |
| v1.4 | Moon day-boundary ambiguity when birth time unknown; weak vs strong pull signals (self-reuse vs friend-forwarded strangers); freeze further paper review |

## Locked product boundary

- Free, no promotion, no fees, no user accounts.
- Audience ≈ 10 Chinese-speaking friends, mobile link.
- Outside career C++ tooling track — amateur timebox only; overtime → stop.

## Five-step review archive (summary)

### Kept

- Birth date / time / place (astronomy inputs);「不知道出生时间」allowed
- MBTI as 16-type dropdown (no built-in quiz)
- Chart visualization via kerykeion SVG
- LLM API one-shot Chinese interpretation (core hypothesis)
- Optional tarot second step on report page only

### Deleted

- astro-seek scraping
- GPT-generated chart images
- Built-in MBTI question bank / scoring
- Accounts, login, history, database
- Custom React/Vercel frontend

### Simplified

- Stack → Streamlit single app
- Chart + drawing → kerykeion alone
- Geocoding → GeoNames via kerykeion (no local gazetteer)

### Accelerated / automation stance

- Local hot reload; fake fixed chart context while tuning prompts
- No CI, cron, or monitoring for the spike; deploy = git push → Streamlit Cloud

## Acceptance & kill criteria

**Quantitative:** two weeks after share, LLM API calls show spontaneous volume beyond first-wave use.

**Qualitative:** ask ~10 friends whether they reused or forwarded. Privacy promise ⇒ no per-user analytics; interviews decide.

**Signal grades:** friend self-reuse = weak (politeness bias); forward to strangers who then use = strong. Commercialization review requires strong signal.

**Stop and archive if:** not done in two weekends; or no spontaneous reuse in two weeks. Real pull → separate career/commercialization review (compliance, payment, privacy at a different scale).

## Open references used in planning

- gsinghjay/zodiac-engine — prompt / interpretation patterns (not FastAPI structure)
- g-battaglia/kerykeion — `context_serializer`, `ReportGenerator`
- catch-twenty2/AstroChart_Analysis — chart field checklist for prompts
- qwq202/Aurora-MBTI — Chinese interpretation tone (quiz parts ignored)
- g-battaglia/Astrologer-API — future paid/non-copyleft data path
