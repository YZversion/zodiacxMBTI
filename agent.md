# Agent guide — zodiacxMBTI

Instructions for AI coding agents working in this repository.

## Project in one sentence

Reversible Streamlit spike: natal chart (kerykeion) + MBTI → streamed Chinese LLM report; optional tarot flip + HTML/PDF export. Friends-only (~10), two-weekend timebox, then measure pull or archive.

## Non-negotiable boundaries

- **Spike, not product.** No accounts, no user history, no marketing, no payment.
- **Anonymous stats only:** `usage_stats.py` → `cache/usage.sqlite` may store aggregate counters (`main_report`, with/without question, `s{n}_hit|miss`). **Never** store birth data, city, MBTI, or question text. Stats failures must not block the report. Operator view: footer expander「运营统计」gated by `STATS_PASSWORD` secret + JSON download (Cloud ephemeral — backup often).
- **Do not rebuild deleted scope:** no astro-seek scraping, no GPT-generated chart images, no built-in MBTI quiz, no React/Vercel custom frontend, no CI/cron/monitoring unless the human explicitly expands the timebox.
- **Secrets never in git.** Keys live in `.streamlit/secrets.toml` (gitignored) or Streamlit Cloud Secrets.
- **Privacy:** do not log or persist birth data.
- **Timebox:** prefer cutting polish over bloating the chart→report path. Two weekends max.

## Preferred stack

| Layer | Choice |
|---|---|
| UI + deploy | Streamlit (`app.py`) + theme CSS via `st.html` |
| Visual tokens | `design_system.py` (`COLORS`, font stacks, `css_variables`) — keep app / HTML export / tarot in sync |
| Chart + SVG | kerykeion wheel-only, `theme="dark"`, `chart_language="CN"` |
| LLM context | `to_context` XML + MBTI — do not hand-roll chart JSON |
| LLM | OpenAI-compatible client (`OPENAI_*` secrets); DeepSeek via `OPENAI_BASE_URL` is fine |
| §4 repair | `generate_question_section` + `upsert_question_section` when life question present but §4 incomplete |
| Tarot logic | `tarot.py` stdlib `random` only — **do not change draw logic for UI** |
| Tarot UI | `tarot_ui.py` + inline `st.html` flip fragment; LuciellaES assets |
| Export | `report_export.py` — full HTML snapshot + text PDF (`fpdf2`); §6 via `split_main_and_extensions` |
| Persona cards | `persona_cards.py` + `persona_cards/persona_cards.json` + offline WebP in `assets/cards/` via `card_image_path` / `manifest.json`; compose with `tools/build_cards.py`. Original art lives locally under `personapicture/` (gitignored). Lookup only — **never LLM-invent nicknames** |
| Anonymous stats | `usage_stats.py` → `cache/usage.sqlite` (counters only; no PII) |
| CN cities | `china_cities.py` + `data/china_cities.json` exact map |

## Implementation rules

1. **`st.session_state`:** cache `chart`, `report_text`, `main_user_question`, tarot results. Tarot = one incremental LLM call only. Fingerprint reset logic must stay intact; only append keys if needed.
2. **Unknown birth time:** noon planets; strip houses/angles from XML; moon 00:00 vs 24:00 ambiguity — never fake certainty. Form default:「不知道出生时间」checked (no fake filled noon).
3. **Place:** CN Chinese city names via `data/china_cities.json` exact map → English for GeoNames; else pinyin/English; country dropdown → ISO (default China=`CN`);「其他」shows 2-letter code field. Ambiguous same-romanization cities stay unmapped.
4. **MBTI:** select starts at「请选择类型」(required);「不确定」at bottom skips cross-analysis. Never treat the sentinel as「不确定」.
5. **Optional `user_question`:** `text_area` above MBTI; included in fingerprint (`.strip()`); passed to `stream_main_report(..., user_question=)`; prefills tarot question on success; result page shows `_render_question_card`.
6. **§4 completeness:** After main stream, if question set and `has_complete_question_section` is false, run `generate_question_section` and `upsert_question_section` before caching. Do not cache a report that dropped the user’s question.
7. **MAIN_SYSTEM:** sections 1–5 + **§6 延伸探索** (exactly 3 `###` items with short answers, not teaser CTAs). UI/HTML render §6 as native `<details>` folds (not `st.expander`). Length: §§1–5 ~1000–1300 chars; each §6 body 80–120. Edit prompts only when the human asks.
8. **TAROT_SYSTEM:** past / present / future / 三张牌共同指向; ~500–650 chars; closing is a hammer (one core tension + one self-question), not more analysis. Red lines: no transit/timing invention, no fabricated trauma origins.
9. **Streaming:** `stream_main_report` / `stream_tarot_report` + `st.write_stream`; optional §4 repair; cache then `st.rerun()`.
10. **Theme CSS:** inject once via `st.html`. Tokens only from `design_system` — do not hardcode old gold `#c9a46c` / cream stacks. **Never** `font-family` on all `span` (breaks expander `.arrow_`). Keep `prefers-reduced-motion` + focus-visible.
11. **Chart display:** wheel-only + CJK fonts; encode SVG as `data:image/svg+xml;base64` `<img>` inside `st.html` — **never** raw `<svg>` in `st.html` (DOMPurify strips it) and **never** `st.iframe` (mobile height often 0).
12. **Tarot display:** inline HTML fragment (no full `<!DOCTYPE html>` document); responsive grid; reduced-motion safe.
13. **Disclaimer / privacy** near submit CTA and in footer.
14. **License:** MIT app code; kerykeion AGPL-3.0 while imported.
15. **Tests:** `tests/test_design_system.py` (tokens ↔ config.toml, export, tarot fragment, natal base64 img, empty date / MBTI sentinel); `tests/test_question_flow.py`; `tests/test_persona_cards.py`; `tests/test_friendly_errors.py`; `tests/test_usage_stats.py`; `tests/test_mentor_batch.py` (sun preview, CN cities, section split, persona PNG).
16. **Persona cards:** show after summary; key = `{MBTI}_{sun_en}` from chart sun + form MBTI;「不确定」→ missing hint, no invented card. Runtime image = `card_image_path` → `assets/cards/webp/{id}.webp` from offline `tools/build_cards.py` (Aries→Libra shipped; 112 cards). No runtime Pillow compose; export HTML may still use `build_persona_card_html` until a follow-up.
17. **Generate CTA:** fixed `key="generate_report"`; label may be `解读我的{太阳}×{MBTI}` or fallback「生成解读». Approximate sun under date is preview-only（以排盘为准）.
18. **Usage + feedback:** `record_successful_report` only once on the just-succeeded path before `report_ready=True`. Section vote buttons for §§1–5 only; session lock per report+section; never double-count.

## Code status

Implemented end-to-end: mentor-batch form UX, anonymous usage + § feedback, CN city map, offline persona-card runtime (`manifest` + WebP; Aries→Libra = 112), password-gated Cloud stats export, optional life-question (+ §4 repair), foldable §6, HTML/PDF export. Cloud live; observation: [SHIP.md](SHIP.md), detail: [log20260727_mentor.md](log20260727_mentor.md).

## Docs to read before coding

Doc map: [`DOCS.md`](DOCS.md). **Do not add `memory.md`** — use `history.md` / `agent.md` instead.

1. [`agent.md`](agent.md) — this file (boundaries first)
2. [architecture.md](architecture.md) — runtime shape
3. [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md) — sealed plan v1.4 (only if revisiting product scope)
4. [history.md](history.md) — decisions + timeline
5. [SHIP.md](SHIP.md) — pre-share checklist
6. [`人设卡_设计稿.md`](人设卡_设计稿.md) — only when working on persona-card content/art

## Out of scope unless asked

Commercialization, payment, Law 25 build-out, English UI, conversational follow-ups, classical aspect rule-banks, Bloom-style scroll video landing (separate static page only if requested), runtime generation of 192 unique persona illustrations, inventing a `memory.md` layer.

## Commit hygiene

- Never commit `.streamlit/secrets.toml` or API keys.
- Do not commit unless the human asks.
- After a non-trivial ship/fix, append one row to `history.md` (not a separate memory file).