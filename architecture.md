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
  • persona card: 192 JSON copy + 12 zodiac master art (HTML)
  • wheel chart via st.html (page DOM; not iframe)
  • report §§1–5 markdown
  • §6 延伸探索 → native HTML <details> folds (not st.expander)
  • export: full HTML page | text PDF  (same design_system tokens)
        │
        └── optional tarot
              draw_three() → CSS 3D flip (st.html fragment)
              → one extra streamed LLM call (cached chart + MBTI + question)
```

## Design principles

| Principle | Implication |
|---|---|
| One-shot report | No accounts, history, or database |
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
chart.py               # GeoNames subject, moon ambiguity, wheel SVG prep
interpret.py           # MAIN_SYSTEM / TAROT_SYSTEM / QUESTION_SECTION_SYSTEM;
                       # stream_* + generate_question_section (§4 repair)
persona_cards.py       # load 192 JSON; lookup MBTI×sun; HTML + zodiac master URI
tarot.py               # 78-card deck + draw_three (logic only)
tarot_ui.py            # name→asset map, flip HTML fragment, base64 faces
report_export.py       # build_report_html / pdf; split_main_and_extensions;
                       # sanitize / has_complete_question_section / upsert_question_section
tests/test_design_system.py
tests/test_question_flow.py
tests/test_persona_cards.py
assets/tarot/rws/      # 78 LuciellaES CC0 faces
assets/fonts/          # NotoSansSC-Regular.ttf for PDF
persona_cards/         # persona_cards.json (192 truth source)
personapicture/zodiac_tarot_masters/v1/  # 12 active 3:5 full-card tarot masters
.streamlit/
  config.toml          # dark theme aligned to COLORS; toolbarMode=minimal
  secrets.toml         # gitignored
  secrets.toml.example
requirements.txt       # streamlit==1.59.2, kerykeion, openai, fpdf2
```

### Adjacent (offline art / prompts; not required at runtime)

```
personapicture/persona_card_img_prompts.json  # 192 unique-art prompts (not generated yet)
personapicture/example/                       # style samples only
personapicture/zodiac_masters/v1/             # archived former master set; not runtime
人设卡_设计稿.md
```

## Form contract

| Field | Control | Notes |
|---|---|---|
| Birth country | select outside form | 中国/美国/…/其他 → ISO;「其他」shows 2-letter input |
| Birth date | date | required |
| Birth time | time +「不知道出生时间」 | checkbox → degraded report |
| Birth city | text | pinyin/English; GeoNames |
| MBTI | 16-type select |「不确定」→ skip cross-analysis |
| Life question | optional text |「最近在纠结的事」; in fingerprint; drives report §4; prefills tarot Q |

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
| Coordinate strip | Live summary of country / date / city / MBTI while filling the form |
| A11y | `prefers-reduced-motion`, `button:focus-visible`, CTA text contrast |
| Question echo | `_render_question_card` when life question was submitted |
| Persona card | `persona_cards.lookup` → HTML (master art + nickname/definition/paradox/exit/pct); MBTI unknown → hint only |
| Summary card | glass HTML via `st.html` |
| Chart | wheel-only SVG via `st.html` (page DOM, not iframe — mobile height-safe); CJK font injection |
| §6 folds | native HTML `<details>` via `st.html` (avoid Streamlit material-icon expander collision) |
| Tarot stage | inline `st.html` fragment (not full document); responsive grid; reduced-motion safe |
| Full page download | self-contained HTML using same `--zx-*` tokens; §6 as closed `<details>` |
| Text PDF | fpdf2 + bundled Noto Sans SC |

## Deployment

- **Dev:** `.\.venv\Scripts\streamlit.exe run app.py` (Windows) / `streamlit run app.py`
- **Prod:** Streamlit Community Cloud, entry `app.py`, Secrets mirrored from local
- **Observability:** Cloud visits + LLM dashboard counts (chart vs tarot)

## License / dependency boundary

| Component | License |
|---|---|
| App code | MIT |
| kerykeion | AGPL-3.0 (while imported) |
| Tarot faces | LuciellaES CC0 |
| Noto Sans SC | SIL OFL |
| Future closed-source path | Astrologer API for chart context |

## Explicitly not in the architecture

Scrapers, generative chart images, MBTI quiz banks, user tables, React SPAs, CI/cron/APM, Bloom-style scroll-video shell inside Streamlit, runtime generation of 192 unique persona illustrations (12 masters + text overlay only).
