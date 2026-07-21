# Agent guide — zodiacxMBTI

Instructions for AI coding agents working in this repository.

## Project in one sentence

Reversible Streamlit spike: natal chart (kerykeion) + MBTI → streamed Chinese LLM report; optional tarot flip + HTML/PDF export. Friends-only (~10), two-weekend timebox, then measure pull or archive.

## Non-negotiable boundaries

- **Spike, not product.** No accounts, no DB, no history, no marketing, no payment.
- **Do not rebuild deleted scope:** no astro-seek scraping, no GPT-generated chart images, no built-in MBTI quiz, no React/Vercel custom frontend, no CI/cron/monitoring unless the human explicitly expands the timebox.
- **Secrets never in git.** Keys live in `.streamlit/secrets.toml` (gitignored) or Streamlit Cloud Secrets.
- **Privacy:** do not log or persist birth data.
- **Timebox:** prefer cutting polish over bloating the chart→report path. Two weekends max.

## Preferred stack

| Layer | Choice |
|---|---|
| UI + deploy | Streamlit (`app.py`) + dark theme CSS via `st.html` |
| Chart + SVG | kerykeion wheel-only, `theme="dark"`, `chart_language="CN"` |
| LLM context | `to_context` XML + MBTI — do not hand-roll chart JSON |
| LLM | OpenAI-compatible client (`OPENAI_*` secrets); DeepSeek via `OPENAI_BASE_URL` is fine |
| Tarot logic | `tarot.py` stdlib `random` only — **do not change draw logic for UI** |
| Tarot UI | `tarot_ui.py` + `components.html` flip stage; LuciellaES assets |
| Export | `report_export.py` — full HTML snapshot + text PDF (`fpdf2`) |

## Implementation rules

1. **`st.session_state`:** cache `chart`, `report_text`, tarot results. Tarot = one incremental LLM call only. Fingerprint reset logic must stay intact; only append keys if needed.
2. **Unknown birth time:** noon planets; strip houses/angles from XML; moon 00:00 vs 24:00 ambiguity — never fake certainty.
3. **Place:** pinyin/English city; country dropdown → ISO (default China=`CN`);「其他」shows 2-letter code field.
4. **MBTI:** 16-type select;「不确定」skips cross-analysis.
5. **MAIN_SYSTEM (locked intent):** psychological-astrology persona; ground-truth only; anti-Barnum (falsifiable behaviors in sections 1–3); four fixed `##` headings. Do not casually rewrite unless the human asks.
6. **Streaming:** use `stream_main_report` / `stream_tarot_report` + `st.write_stream`; persist full text to session after stream; `st.rerun()` for clean cached view.
7. **Theme CSS:** inject with `st.html`, once. **Never** set `font-family` on all `span` — breaks expander `.arrow_` icon fonts.
8. **Chart display:** wheel-only + CJK font injection; square iframe; avoid full CN side-tables (they overlap on mobile).
9. **Disclaimer / privacy** footer always present.
10. **License:** MIT app code; kerykeion AGPL-3.0 while imported.

## Code status

Implemented end-to-end locally. Remaining human path: secrets → Cloud deploy → friend canary → quiet two-week observation.

## Docs to read before coding

1. [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md) — sealed plan v1.4
2. [architecture.md](architecture.md) — runtime shape
3. [history.md](history.md) — decisions + timeline

## Out of scope unless asked

Commercialization, payment, Law 25 build-out, English UI, conversational follow-ups, classical aspect rule-banks, Bloom-style scroll video landing (separate static page only if requested).

## Commit hygiene

- Never commit `.streamlit/secrets.toml` or API keys.
- Do not commit unless the human asks.
