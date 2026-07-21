# Agent guide — zodiacxMBTI

Instructions for AI coding agents working in this repository.

## Project in one sentence

Reversible Streamlit spike: natal chart (kerykeion) + MBTI → one-shot Chinese LLM report; optional tarot add-on. Friends-only (~10 users), two-weekend timebox, then measure pull or archive.

## Non-negotiable boundaries

- **Spike, not product.** No accounts, no DB, no history, no marketing, no payment.
- **Do not rebuild deleted scope:** no astro-seek scraping, no GPT-generated chart images, no built-in MBTI quiz, no React/Vercel custom frontend, no CI/cron/monitoring unless the human explicitly expands the timebox.
- **Secrets never in git.** Keys live in `.streamlit/secrets.toml` (gitignored) or Streamlit Cloud Secrets. If a key appears in a diff, stop and remove it.
- **Privacy:** do not log or persist birth data. No print of PII to logs.
- **Timebox:** prefer cutting tarot over bloating the chart→report main path. Two weekends max; unfinished → stop and archive.

## Preferred stack

| Layer | Choice |
|---|---|
| UI + deploy | Single Streamlit app (`app.py` or a thin module split if needed) |
| Chart + SVG | `kerykeion` + GeoNames username for place lookup |
| LLM context | kerykeion `context_serializer` (XML) + MBTI field — do not hand-roll JSON chart dumps |
| LLM | OpenAI or Anthropic API, Chinese long-form sections fixed in prompt |
| Tarot | stdlib `random` only; 78 Rider–Waite; 3 cards past/present/future; upright/reversed |

## Implementation rules

1. **`st.session_state` from day one.** Cache chart context, SVG, and main report text. Tarot must only add one incremental LLM call — never re-run the full chart + report pipeline on widget interaction.
2. **Unknown birth time:** compute planetary signs at 12:00; omit ascendant and houses; state that clearly at the top of the report. **Moon:** if sign differs between 00:00 and 24:00 that day, say both possibilities — never fake certainty.
3. **Place input:** prompt users for pinyin/English city names (e.g. `Shanghai`). On GeoNames failure, suggest a larger nearby city.
4. **MBTI:** 16-type select; optional「不确定」skips MBTI cross-analysis.
5. **Report sections (fixed in prompt):** (1) core portrait / resonance (2) tension points (3) relationship & communication (4) one-line stage advice. Tone: concrete, little jargon; explain terms in plain Chinese on first use.
6. **Disclaimer footer** always present (entertainment / self-exploration only).
7. **License awareness:** app code is MIT; kerykeion is AGPL-3.0. Do not advise closed-source distribution while importing the library; commercialization path is Astrologer API swap.

## What “done” means for weekend one

Local (then Cloud) path: form → chart + SVG → Chinese report, including unknown-time and place-failure copy. Prompt quality is the main product work — iterate on fixed serializer output before polishing UI.

**Code status:** the path above is implemented in `app.py` / `chart.py` / `interpret.py` / `tarot.py`. Remaining human steps: fill secrets, `streamlit run app.py`, deploy Cloud, friend test.

## Docs to read before coding

1. [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md) — sealed plan v1.4
2. [architecture.md](architecture.md) — runtime shape
3. [history.md](history.md) — why decisions were locked

## Out of scope for agents unless asked

Commercialization review, payment, Law 25 compliance build-out, English UI, conversational follow-ups, chart art polish, expanding beyond the friends circle.

## Commit hygiene

- First real code commit must not contain secrets.
- Prefer small, reversible commits aligned to the weekend plan.
- Do not commit unless the human asks.
