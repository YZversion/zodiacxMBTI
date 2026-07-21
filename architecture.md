# Architecture

Spike architecture for **zodiacxMBTI**: one straight pipeline, no persistent state.

## System diagram

```
Streamlit form (mobile-first Chinese UI)
        │
        ▼
kerykeion (Swiss Ephemeris + GeoNames)
  • planet signs / houses / ascendant
  • SVG natal chart
  • context_serializer → LLM-oriented XML
        │
        ▼
LLM API  (chart XML + MBTI → Chinese sectioned report)
        │
        ▼
Result page: SVG + report sections + privacy/disclaimer
        │
        └── optional: 「再抽三张牌」
              random 3/78 + orientation
              → one extra LLM call (cards + cached chart context + MBTI)
```

## Design principles

| Principle | Implication |
|---|---|
| One-shot report | No accounts, history, or database |
| One Python surface | Streamlit only — no separate frontend/backend |
| One chart library | kerykeion for math + SVG + serializer |
| Cache across reruns | `st.session_state` holds chart context, SVG, and main report so widgets (esp. tarot) do not double-bill the LLM |
| Honest degradation | Unknown birth time and moon sign-change are explained, not invented |
| Public repo + secrets outside git | `.streamlit/secrets.toml` / Cloud Secrets; API spend cap ≈ $10 |

## Modules

```
app.py                 # Streamlit entry: form, orchestration, result UI
chart.py               # kerykeion wrapper, unknown-time / moon logic, serializer
interpret.py           # LLM prompts + main report + tarot follow-up
tarot.py               # deck, shuffle, three-card draw (stdlib random)
.streamlit/
  secrets.toml         # gitignored — API keys, GeoNames username
  secrets.toml.example
  config.toml
requirements.txt
```

## Form contract

| Field | Control | Notes |
|---|---|---|
| Birth date | date | required |
| Birth time | time +「不知道出生时间」 | checkbox → degraded report |
| Birth place | city text + ISO nation (default `CN`) | pinyin/English city; GeoNames |
| MBTI | 16-type select |「不确定」→ skip MBTI cross-analysis |

### Unknown birth time

- Planets at local 12:00 that day.
- Omit ascendant and houses; open with an explicit one-line caveat.
- Moon: compare sign at 00:00 vs 24:00; if different, report both and refuse to pick one.

## LLM I/O

**Input:** kerykeion `context_serializer` XML + MBTI (if known).

**Output sections (prompt-enforced):**

1. 核心性格画像（共振）
2. 星盘与 MBTI 的张力点
3. 关系与沟通风格
4. 当前阶段的一句话建议

**Tarot follow-up prompt:** three cards (past / present / future) with orientation, optional user question, must weave chart context + MBTI.

## Deployment

- **Dev:** `streamlit run app.py`
- **Prod:** Streamlit Community Cloud from the public GitHub repo
- **Observability (spike-grade):** Cloud visit stats + LLM dashboard call counts (baseline on launch day; revisit at two weeks). Chart vs tarot calls counted separately.

## License / dependency boundary

| Component | License posture |
|---|---|
| This repo’s application code | MIT |
| kerykeion (imported) | AGPL-3.0 — open distribution expected while using the library |
| Future commercialization | Swap chart data source to Astrologer API (`/context/*`) to leave copyleft |

## Explicitly not in the architecture

Scraper clients, generative chart images, MBTI item banks, user tables, React SPAs, CI pipelines, cron jobs, production APM.
