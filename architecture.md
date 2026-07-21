# Architecture

Spike architecture for **zodiacxMBTI**: one straight pipeline, no persistent state.

## System diagram

```
Streamlit form (dark starfield UI, mobile Chinese)
        │
        ▼
kerykeion (Swiss Ephemeris + GeoNames)
  • planet signs / houses / ascendant (houses omitted if time unknown)
  • dark wheel-only SVG (CN labels)
  • to_context → LLM-oriented XML
        │
        ▼
LLM API stream  (XML + MBTI + optional user_question → Chinese report)
  • cached in st.session_state.report_text
        │
        ▼
Result page
  • glass summary card (Sun / Moon / Asc × MBTI + §5 advice)
  • expandable wheel chart
  • full report markdown
  • export: full HTML page | text PDF
        │
        └── optional tarot
              draw_three() → CSS 3D flip (components.html)
              → one extra streamed LLM call (cached chart + MBTI + question)
```

## Design principles

| Principle | Implication |
|---|---|
| One-shot report | No accounts, history, or database |
| One Python surface | Streamlit only |
| One chart library | kerykeion for math + SVG + serializer |
| Cache across reruns | session_state prevents double LLM billing |
| Honest degradation | Unknown time / moon sign-change explained |
| Secrets outside git | `.streamlit/secrets.toml` / Cloud Secrets; spend cap |
| OpenAI-compatible LLM | DeepSeek works via `OPENAI_BASE_URL` |

## Modules

```
app.py                 # UI, theme CSS (st.html), orchestration, downloads
chart.py               # GeoNames subject, moon ambiguity, wheel SVG prep
interpret.py           # MAIN_SYSTEM / TAROT_SYSTEM, stream_* generators
tarot.py               # 78-card deck + draw_three (logic only)
tarot_ui.py            # name→asset map, flip HTML, base64 faces
report_export.py       # build_report_html, build_report_pdf
assets/tarot/rws/      # 78 LuciellaES CC0 faces
assets/fonts/          # NotoSansSC-Regular.ttf for PDF
.streamlit/
  config.toml          # dark theme colors
  secrets.toml         # gitignored
  secrets.toml.example
requirements.txt       # streamlit, kerykeion, openai, fpdf2
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

**MAIN_SYSTEM highlights:** psychological-astrology persona; ground truth only; anti-Barnum; hook first sentence per section; money section = 2nd/6th/10th + Saturn/Jupiter behavior (no fortune predictions). Headings:

1. 核心性格画像（≤ two paragraphs）  
2. 金钱与事业风格  
3. 关系与沟通风格  
4. 关于你正在纠结的事（only if `user_question` set; should be longest）  
5. 当前阶段的一句话建议  

If no question: skip §4 entirely (heading omitted); still emit §5.

**Streaming:** OpenAI-compatible `stream=True` → `st.write_stream` → cache full string.

**Tarot:** past/present/future + orientation; optional question (prefilled from main form); weave chart + MBTI. `TAROT_SYSTEM` unchanged from early spike.

## UI / export

| Piece | Mechanism |
|---|---|
| Atmosphere | CSS starfield + vignette + grain on `stAppViewContainer` |
| Fonts | Instrument Serif + Noto Serif SC (titles); Space Grotesk + Noto Sans SC (body) |
| Summary card | glassmorphism HTML via `st.html` |
| Chart | wheel-only SVG in expander iframe; CJK font injection |
| Tarot stage | `components.html` flip animation; interpretation below iframe |
| Full page download | self-contained HTML (SVG + card images + report) |
| Text PDF | fpdf2 + bundled Noto Sans SC |

## Deployment

- **Dev:** `streamlit run app.py`
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

Scrapers, generative chart images, MBTI quiz banks, user tables, React SPAs, CI/cron/APM, Bloom-style scroll-video shell inside Streamlit.
