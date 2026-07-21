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
5. **Optional `user_question`:** form field「最近在纠结的事」; included in fingerprint; passed to `stream_main_report(..., user_question=)`; prefills tarot question on success.
6. **MAIN_SYSTEM:** psychological-astrology persona; ground-truth + anti-Barnum (rules 1–6 keep intent); sections = 画像 / 金钱与事业 / 关系 / 纠结(optional) / 一句话建议; hook-sentence + no fortune-telling in money section. Edit only when the human asks.
7. **Streaming:** `stream_main_report` / `stream_tarot_report` + `st.write_stream`; cache then `st.rerun()`.
8. **Theme CSS:** `st.html` once. **Never** `font-family` on all `span` (breaks expander `.arrow_`).
9. **Chart display:** wheel-only + CJK font injection; square iframe.
10. **Disclaimer / privacy** footer always present.
11. **License:** MIT app code; kerykeion AGPL-3.0 while imported.

## Code status

Implemented end-to-end locally (including optional life-question section). Human path: [SHIP.md](SHIP.md) → Cloud → canary → quiet two weeks.

## Docs to read before coding

1. [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md) — sealed plan v1.4
2. [architecture.md](architecture.md) — runtime shape
3. [history.md](history.md) — decisions + timeline
4. [SHIP.md](SHIP.md) — pre-share checklist

## Out of scope unless asked

Commercialization, payment, Law 25 build-out, English UI, conversational follow-ups, classical aspect rule-banks, Bloom-style scroll video landing (separate static page only if requested).

## Commit hygiene

- Never commit `.streamlit/secrets.toml` or API keys.
- Do not commit unless the human asks.
