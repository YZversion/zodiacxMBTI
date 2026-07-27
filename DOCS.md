# Docs map — zodiacxMBTI

Which markdown to open before changing code. Keep this list short; prefer updating an existing file over inventing a new one.

## Do agents need `memory.md`?

**No.** For this spike, durable agent context already lives elsewhere:

| Need | File |
|---|---|
| Rules / red lines / stack | [`agent.md`](agent.md) |
| Runtime shape | [`architecture.md`](architecture.md) |
| What we decided & when | [`history.md`](history.md) |
| Sealed product plan | [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md) |

A separate `memory.md` usually duplicates the timeline and goes stale. If something must stick across chat sessions, append one row to `history.md` or one rule to `agent.md` — do not create a fourth “memory” surface unless the human explicitly asks.

## Core (read for almost every coding task)

| Doc | Role | Update when |
|---|---|---|
| [`README.md`](README.md) | Human entry: what / run / Cloud URL / feature table | Public behavior or run steps change |
| [`agent.md`](agent.md) | Agent contract: boundaries, stack, implementation rules | Rules or preferred stack change |
| [`architecture.md`](architecture.md) | Pipeline, modules, LLM I/O, UI/export | Runtime path or module layout change |
| [`history.md`](history.md) | Decision + spike timeline | Non-trivial ship / fix / product call |

## Ship & plan

| Doc | Role |
|---|---|
| [`SHIP.md`](SHIP.md) | Pre-share checklist + observation cadence |
| [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md) | Sealed plan **v1.4** — do not reopen paper review; code wins after seal |

## Content / growth (only when that work is in scope)

| Doc | Role |
|---|---|
| [`人设卡_设计稿.md`](人设卡_设计稿.md) | Persona-card copy/layout rules; JSON is truth for 192 cards |
| [`小红书测试_物料与生态速览.md`](小红书测试_物料与生态速览.md) | XHS posting boundaries; no outbound links |
| [`persona_cards/persona_cards_预览.md`](persona_cards/persona_cards_预览.md) | Human preview of 192 cards — edit JSON, then regenerate preview if needed |
| [`personapicture/zodiac_tarot_masters/v1/README.md`](personapicture/zodiac_tarot_masters/v1/README.md) | Active 12 persona master art (runtime) |
| [`personapicture/zodiac_masters/v1/README.md`](personapicture/zodiac_masters/v1/README.md) | Archived former masters — not runtime |

## Asset attributions (rarely edited)

| Doc | Role |
|---|---|
| [`assets/tarot/ATTRIBUTION.md`](assets/tarot/ATTRIBUTION.md) | LuciellaES CC0 RWS faces |
| [`assets/fonts/README.md`](assets/fonts/README.md) | Noto Sans SC for PDF |

## Agent reading order (default)

1. `agent.md` — boundaries first  
2. `architecture.md` — where to change code  
3. Relevant module / test  
4. `history.md` — only if the task touches a past decision  

Persona / XHS / art prompts: open the matching content doc above; do not load them by default.
