# Architecture

Spike architecture for **zodiacxMBTI**: one straight pipeline, no persistent state.

Doc map: [`DOCS.md`](DOCS.md). Agent rules: [`agent.md`](agent.md).

## System diagram

```
Streamlit form (night-sky coordinate UI + hero, mobile Chinese)
        │
        ▼
kerykeion (Swiss Ephemeris + GeoNames)
  • planet signs / houses / ascendant (houses omitted if time unknown)
  • dark wheel-only SVG (CN labels)
  • to_context → LLM-oriented XML
        │
        ▼
LLM API stream  (XML + MBTI + optional user_question → Chinese report)
  • if user_question set but §4 missing/short:
      generate_question_section (extra non-stream call)
      → upsert_question_section before §5
  • cached in st.session_state.report_text
        │
        ▼
Result page
  • optional「本次问题」echo card
  • glass summary card (Sun / Moon / Asc × MBTI + §5 advice)
  • persona card: 192 JSON + art (MBTI×sign PNG if shipped, else 12 zodiac master)
  • wheel chart as base64 img via st.html (not raw SVG / not iframe)
  • report §§1–5 markdown + per-section 准/不像我 → usage_stats
  • §6 延伸探索 → native HTML <details> folds (not st.expander)
  • public usage caption + optional STATS_PASSWORD operator panel + JSON export
  • export: full HTML page | text PDF  (same design_system tokens)
        │
        └── optional tarot
              draw_three() → CSS 3D flip (st.html fragment)
              → one extra streamed LLM call (cached chart + MBTI + question)
```

## Design principles

| Principle | Implication |
|---|---|
| One-shot report | No accounts or user profiles; **anonymous aggregate counters only** (no birth/question text) |
| One Python surface | Streamlit only |
| One chart library | kerykeion for math + SVG + serializer |
| Shared visuals | `design_system.py` tokens for app / HTML export / tarot stage |
| Cache across reruns | session_state prevents double LLM billing |
| Honest degradation | Unknown time / moon sign-change explained |
| Secrets outside git | `.streamlit/secrets.toml` / Cloud Secrets; spend cap |
| OpenAI-compatible LLM | DeepSeek works via `OPENAI_BASE_URL` |

## Modules

```
app.py                 # UI, THEME_CSS via st.html, hero, coordinate strip, orchestration
design_system.py       # COLORS, font stacks, css_variables() → --zx-*
chart.py               # GeoNames subject, moon ambiguity, wheel SVG prep; CN city via china_cities
china_cities.py        # data/china_cities.json exact zh → en for GeoNames
sun_preview.py         # approximate sun sign for form hints (not kerykeion)
usage_stats.py         # cache/usage.sqlite counters; build_stats_snapshot for operator export
interpret.py           # MAIN_SYSTEM / TAROT_SYSTEM / QUESTION_SECTION_SYSTEM;
                       # stream_* + generate_question_section (§4 repair)
persona_cards.py       # 192 JSON; card_image_path (manifest WebP); art helpers kept for export;
                       # HTML, st.image path, share PNG
tarot.py               # 78-card deck + draw_three (logic only)
tarot_ui.py            # name→asset map, flip HTML fragment, base64 faces
report_export.py       # build_report_html / pdf; split_main_and_extensions;
                       # sanitize / has_complete_question_section / upsert_question_section
tests/test_design_system.py
tests/test_question_flow.py
tests/test_persona_cards.py
tests/test_friendly_errors.py
tests/test_usage_stats.py
tests/test_mentor_batch.py
tests/test_app_validation_smoke.py
data/china_cities.json
persona_cards/         # persona_cards.json (192 truth source)
assets/cards/          # offline composed WebP + manifest.json
personapicture/zodiac_tarot_masters/v1/  # 12 fallback masters (local / gitignored)
personapicture/mbti_tarot_cards/{sign}/v1/ # per-sign 16 MBTI art (compose input)
assets/tarot/rws/      # 78 LuciellaES CC0 faces
assets/fonts/          # NotoSansSC-Regular.ttf for PDF
.streamlit/
  config.toml          # dark theme aligned to COLORS; toolbarMode=minimal
  secrets.toml         # gitignored
  secrets.toml.example
requirements.txt       # streamlit==1.59.2, kerykeion, openai, fpdf2, pillow
```

### Adjacent (offline art / prompts; not required at runtime)

```
personapicture/persona_card_img_prompts.json  # 192 unique-art prompts (not generated yet)
personapicture/mbti_tarot_cards/            # 16×MBTI per-sign sets (SOP in README)
personapicture/example/                       # style samples only
personapicture/zodiac_masters/v1/             # archived former master set; not runtime
人设卡_设计稿.md
```

## Form contract

| Field | Control | Notes |
|---|---|---|
| Birth country | select outside form | 中国/美国/…/其他 → ISO;「其他」shows 2-letter input |
| Birth date | date | required; default empty |
| Birth time | time +「不知道出生时间」 | default checkbox **on** → degraded report |
| Birth city | text | CN 中文 / pinyin / English; `maybe_resolve_city` when nation=CN |
| MBTI | select | sentinel「请选择类型」;「不确定」last → skip cross-analysis |
| Life question | optional text_area | above MBTI; in fingerprint; drives §4; prefills tarot Q |

### Unknown birth time

- Planets at local 12:00.
- Strip houses/angles from XML; UI notes omit ascendant/houses.
- Moon: 00:00 vs next-day 00:00; if different, report both.

## LLM I/O

**Input:** `to_context` XML (+ moon_ambiguity if needed) + MBTI + optional `user_question`.

**MAIN_SYSTEM highlights:** psychological-astrology persona; ground truth only; anti-Barnum; section-open hooks = concrete personality contradictions (thesis of the section); money section = 2nd/6th/10th + Saturn/Jupiter behavior (no fortune predictions); origin + exit red lines. Headings:

1. 核心性格画像（180–250）  
2. 金钱与事业风格（220–300）  
3. 关系与沟通风格（220–300）  
4. 关于你正在纠结的事（only if `user_question` set; 350–450）  
5. 当前阶段的一句话建议（30–45）  
6. 延伸探索 — exactly 3 `###` items (title + 80–120 字解析 each): relationship / money-career tension / synastry sketch. No「想知道吗」teasers.

If no question: skip §4 entirely (heading omitted); still emit §5 and §6.  
UI/HTML: `split_main_and_extensions` keeps §§1–5 in the main prose and renders §6 as collapsed expanders / `<details>`.

**Streaming:** OpenAI-compatible `stream=True` → `st.write_stream` → sanitize → optional §4 repair → cache full string → rerun.

**§4 repair:** If `user_question` is set and `has_complete_question_section` fails (missing or body under 80 chars), one extra non-stream `generate_question_section` call fills §4 via `upsert_question_section` (inserted before §5). Failure aborts without caching a partial report.

**Tarot:** past / present / future / 三张牌共同指向 (~500–650 chars); closing hammer = one core tension + one self-question; optional question (prefilled from main form); weave chart + MBTI. No transit invention. Do not append a main-report-style「延伸探索」block to tarot text.

## UI / export

| Piece | Mechanism |
|---|---|
| Tokens | `design_system.COLORS` — night navy `#0b1626`, parchment text `#e7ddc9`, mint CTA `#c7d9d2`, copper/coordinate accents |
| Atmosphere | CSS grid + deep gradient on `stAppViewContainer` (no remote fonts; grain animation removed) |
| Fonts | Display = Kaiti / Noto Serif SC; body = Noto Sans SC; data = Space Grotesk / mono |
| Hero | Brand-first first viewport: eyebrow + title + one lede |
| Coordinate strip | Live summary of date / time / city / MBTI while filling the form |
| Sun / combo hints | `sun_preview.approximate_sun_sign_zh` (labeled 以排盘为准) |
| Generate CTA | `st.button(..., key="generate_report")`; dynamic label when date+MBTI set |
| Usage caption | `get_usage_stats` → prominent HTML strip (form + result page) |
| Section feedback | `split_numbered_sections` + buttons §1–5; `record_section_feedback`; session lock |
| Operator stats | Footer expander if `STATS_PASSWORD` set; table + JSON download (`build_stats_snapshot`) |
| A11y | `prefers-reduced-motion`, `button:focus-visible`, CTA text contrast |
| Question echo | `_render_question_card` when life question was submitted |
| Persona card | lookup `manifest.json` → `card_image_path` → `st.image` + text block; all 12 signs live (192 WebP cards) |
| Summary card | glass HTML via `st.html` |
| Chart | wheel-only SVG as base64 `<img>` via `st.html` (DOMPurify strips raw SVG; no iframe) + CJK font injection |
| §6 folds | native HTML `<details>` via `st.html` (avoid Streamlit material-icon expander collision) |
| Tarot stage | inline `st.html` fragment (not full document); responsive grid; reduced-motion safe |
| Full page download | self-contained HTML using same `--zx-*` tokens; §6 as closed `<details>` |
| Text PDF | fpdf2 + bundled Noto Sans SC |

## Deployment

- **Dev:** `.\.venv\Scripts\streamlit.exe run app.py` (Windows) / `streamlit run app.py`
- **Prod:** Streamlit Community Cloud, entry `app.py`, Secrets mirrored from local
- **Observability:** Cloud visits + LLM dashboard counts; in-app `usage_stats` (ephemeral on Cloud — export JSON); optional `GENERATION_COUNT_BASE` / `QUESTION_COUNT_BASE` in Secrets

## License / dependency boundary

| Component | License |
|---|---|
| App code | MIT |
| kerykeion | AGPL-3.0 (while imported) |
| Tarot faces | LuciellaES CC0 |
| Noto Sans SC | SIL OFL |
| Future closed-source path | Astrologer API for chart context |

## Explicitly not in the architecture

Scrapers, generative chart images, MBTI quiz banks, user tables, React SPAs, CI/cron/APM, Bloom-style scroll-video shell inside Streamlit. Per-sign 192 unique art ships via offline compose (`mbti_tarot_cards/` → `assets/cards/webp/`); all 12 signs live in manifest (192 cards).
