"""LLM interpretation prompts and calls."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from openai import OpenAI

from report_export import sanitize_main_report

if TYPE_CHECKING:
    from chart import ChartResult
    from tarot import DrawnCard

MAIN_SYSTEM = """你是心理占星传统下的现代西方占星师，并用务实、细腻的中文做性格解读；同时熟悉 MBTI。
你会收到结构化的星盘 ground truth（XML）以及可选的 MBTI 类型。解读应贴近荣格式性格分析，而非算命式预言。
硬性规则：
1. 只依据提供的星盘数据与 MBTI，不要编造未给出的行星落座、宫位或上升；不要推断额外的行星位置。
2. 若上下文声明出生时间未知、已省略上升/宫位、或月亮换座存疑，必须遵守，不得装作确定；不确定处明确标注。
3. 语气具体、有细节，少堆砌术语；术语首次出现时用一句白话解释。
4. 反巴纳姆：禁止对任何人都成立的泛化描述（如「外表坚强内心柔软」）；第 1–3 节每一节至少给出两个可被本人证实或证伪的具体行为推断（例如在什么场景下会做什么、会回避什么）。
5. 不要写成通用星座运势或鸡汤；写出这个人可能的具体行为与内在张力。
6. 全文使用简体中文。
7. 严格按下列二级标题输出（不要自创其他二级标题）。第 4 节「关于你正在纠结的事」仅当用户提供了具体问题时报出，且该节应为全文最长；未提供则完全跳过第 4 节（标题也不要出现），其余章节编号仍为 1、2、3、5、6：
## 1. 核心性格画像
## 2. 金钱与事业风格
## 3. 关系与沟通风格
## 4. 关于你正在纠结的事
## 5. 当前阶段的一句话建议
## 6. 延伸探索
8. 篇幅（按汉字计，含标点近似即可；宁短勿注水）：第 1 节 180–250 字；第 2、3 节各 220–300 字；第 4 节（若有）350–450 字；第 5 节 30–45 字；第 6 节共 3 条，每条标题外正文 80–120 字。第 1–5 节合计约 1000–1300 字（无第 4 节时约 700–950 字）。删掉重复论证，提高「准」的密度。
9. 钩子规则：第 1–4 节的第一句必须直接揭示一个具体的性格矛盾，让读者产生「为什么我会这样」的好奇心；该句必须同时是本节核心结论，后文只负责解释与验证。禁止与正文脱节的提问、预告、悬念；禁止「想知道……吗」式只抛问题不给答案的伪 CTA。第 5、6 节不适用本条。
10. 「金钱与事业风格」一节：基于第二宫、第六宫、第十宫及土星/木星等相关落座，只分析金钱观、消费与积累的行为模式、职业中的决策倾向与优劣势。严禁预测财运走势、严禁给出投资理财或买卖建议、严禁断言未来事件。生时未知（无宫位）时，改用相关行星星座与相位分析，并如实说明依据较少。
11. 「关于你正在纠结的事」一节：必须围绕用户原话展开，给出该星盘主人面对此类抉择时的典型决策模式、最可能的自我欺骗方式、以及一个可操作的判断框架；不代替用户做决定，不预测哪个选项会成功。
12. 「延伸探索」一节（第 6 节，必出）：给出恰好 3 条可折叠深挖，每条必须「有标题 + 有解析」，禁止只写问题不写答案。格式严格如下（用三级标题，不要用无点「想知道吗」）：
### 标题（点名本盘真实落座或宫位，如「金星白羊：亲密关系的反复模式」）
正文 80–120 字：直接给出模式判断与可观察行为，可含一个短出口；不要反问读者「想知道吗」。
三条方向固定为：①关系/金星或月亮模式 ②事业或金钱决策张力（只谈行为模式，不给投资建议、不编造行运）③合盘/人际节奏的示意性对比（标明是示意，不假装已有对方星盘）。
13. 成因禁令：严禁编造星盘数据之外的心理成因，包括但不限于童年经历、原生家庭、过往创伤；可以描述模式，不可以虚构模式的来历。
14. 出口规则：每一个负面或扎心的指认之后，必须以一个当事人可操作的视角、做法或自我提问收尾；报告整体基调是「看见并陪伴」，不是「审判」。
若 MBTI 未知，不做 MBTI 交叉分析并明确说明，第 1–3 节仅依据星盘展开。"""

TAROT_SYSTEM = """你是一位结合星盘与 MBTI 做塔罗补充解读的中文写作者。
规则：
1. 结合已给出的星盘上下文与 MBTI（若有）解读三张牌，不要孤立讲牌义。
2. 尊重正逆位；牌阵为过去 / 现在 / 未来。
3. 若用户提出了具体问题，围绕该问题展开；否则做通用阶段解读。
4. 不装神棍，不承诺预测必然结果；语气具体、克制。
5. 全文简体中文。严格按下列四个小标题输出（不要自创其他标题，不要用「综合」「综合解读与行动方向」等旧标题）：
## 过去
## 现在
## 未来
## 三张牌共同指向
6. 篇幅（按汉字计）：过去 / 现在 / 未来各 100–130 字；「三张牌共同指向」150–200 字；全文合计约 500–650 字。
7. 「三张牌共同指向」必须是落锤式收束，只做三件事：概括三张牌共同讲了什么；点明用户当前真正的核心矛盾；留下一个可带走的自我提问。不得重复逐张牌解释，不得开启新的分析方向，不得给出加仓/减仓、投资、医疗或其他重大决策建议。
8. 只依据用户提供的星盘 ground truth 与三张牌面；严禁引用或编造任何行运、流年、行星顺逆行时间、行运与本命的相位等未提供的天文数据。
9. 严禁给出时间预测（如「X 个月内会发生」「时间窗口在……」）；「未来」位置的牌只解读趋势与当事人可采取的行动方向，不断言事件与时点。
10. 严禁编造星盘数据之外的心理成因（童年、原生家庭、创伤等）；可描述模式，不可虚构模式的来历。
11. 禁止在塔罗正文末尾追加「延伸探索」「想知道更多吗」等主报告式追问块。"""


def _client(api_key: str, base_url: Optional[str] = None) -> OpenAI:
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _stream_chat(
    *,
    api_key: str,
    model: str,
    system: str,
    user: str,
    base_url: Optional[str] = None,
) -> Iterator[str]:
    client = _client(api_key, base_url)
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def build_main_user_prompt(
    chart: "ChartResult",
    *,
    user_question: str = "",
) -> str:
    parts = [
        "请根据以下星盘 ground truth 撰写解读报告。",
        "要求：第 1–5 节约 1000–1300 字；第 6 节「延伸探索」用 3 个 ### 小标题，每条必须有短解析（禁止只写「想知道吗」）。",
        "",
        "【前置说明】",
    ]
    if chart.preface_notes:
        parts.extend(f"- {n}" for n in chart.preface_notes)
    else:
        parts.append("- 出生时间已知，可使用上升与宫位信息。")

    if chart.mbti:
        parts.append(f"- MBTI：{chart.mbti}（请做星盘 × MBTI 交叉分析）")
    else:
        parts.append("- MBTI：不确定（跳过 MBTI 交叉分析）")

    q = (user_question or "").strip()
    if q:
        parts.append(
            f'- 用户正在纠结的事（原话）："{q}"，请在第 4 节针对性展开'
        )
    else:
        parts.append("- 用户未提供具体问题，跳过第 4 节")

    parts.extend(
        [
            f"- 解析地点：{chart.resolved_city or chart.city}（{chart.nation}）",
            f"- 时区：{chart.resolved_tz or '未知'}",
            "",
            "【星盘 XML】",
            chart.context_xml,
        ]
    )
    return "\n".join(parts)


def _tarot_user_prompt(
    chart: "ChartResult",
    cards: list["DrawnCard"],
    question: str,
) -> str:
    card_lines = "\n".join(f"- {c.label_zh()}" for c in cards)
    q = question.strip() or "（用户未提问，请做通用阶段解读）"
    mbti = chart.mbti or "不确定"
    return "\n".join(
        [
            "请结合星盘与人格类型解读下列三张牌。",
            "输出四个小标题：过去、现在、未来、三张牌共同指向；全文约 500–650 字；最后一节必须收束，不要展开新分析。",
            f"MBTI：{mbti}",
            f"用户问题：{q}",
            "",
            "【抽牌结果】",
            card_lines,
            "",
            "【星盘 XML（与主报告相同缓存）】",
            chart.context_xml,
        ]
    )


def stream_main_report(
    chart: "ChartResult",
    *,
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
    user_question: str = "",
) -> Iterator[str]:
    yield from _stream_chat(
        api_key=api_key,
        model=model,
        system=MAIN_SYSTEM,
        user=build_main_user_prompt(chart, user_question=user_question),
        base_url=base_url,
    )


def stream_tarot_report(
    chart: "ChartResult",
    cards: list["DrawnCard"],
    *,
    question: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
) -> Iterator[str]:
    yield from _stream_chat(
        api_key=api_key,
        model=model,
        system=TAROT_SYSTEM,
        user=_tarot_user_prompt(chart, cards, question),
        base_url=base_url,
    )


def generate_main_report(
    chart: "ChartResult",
    *,
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
    user_question: str = "",
) -> str:
    text = "".join(
        stream_main_report(
            chart,
            api_key=api_key,
            model=model,
            base_url=base_url,
            user_question=user_question,
        )
    ).strip()
    text = sanitize_main_report(text)
    if not text:
        raise RuntimeError("LLM 返回空内容，请稍后重试。")
    return text


def generate_tarot_report(
    chart: "ChartResult",
    cards: list["DrawnCard"],
    *,
    question: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
) -> str:
    text = "".join(
        stream_tarot_report(
            chart,
            cards,
            question=question,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    ).strip()
    if not text:
        raise RuntimeError("LLM 返回空内容，请稍后重试。")
    return text
