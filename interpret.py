"""LLM interpretation prompts and calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from openai import OpenAI

if TYPE_CHECKING:
    from chart import ChartResult
    from tarot import DrawnCard

MAIN_SYSTEM = """你是一位务实、细腻的中文性格解读写作者，同时熟悉西洋占星与 MBTI。
你会收到结构化的星盘 ground truth（XML）以及可选的 MBTI 类型。
硬性规则：
1. 只依据提供的星盘数据与 MBTI，不要编造未给出的行星落座、宫位或上升。
2. 若上下文声明出生时间未知、已省略上升/宫位、或月亮换座存疑，必须遵守，不得装作确定。
3. 语气具体、有细节，少堆砌术语；术语首次出现时用一句白话解释。
4. 不要写成通用星座运势或鸡汤；写出这个人可能的具体行为与内在张力。
5. 全文使用简体中文。
6. 严格按下列四个二级标题输出（不要增减标题）：
## 1. 核心性格画像
## 2. 星盘与 MBTI 的张力点
## 3. 关系与沟通风格
## 4. 当前阶段的一句话建议
若 MBTI 未知，第 1、2 节只做星盘分析，并明确说明未做 MBTI 交叉分析；第 2 节可改为「星盘内的张力点」。"""

TAROT_SYSTEM = """你是一位结合星盘与 MBTI 做塔罗补充解读的中文写作者。
规则：
1. 结合已给出的星盘上下文与 MBTI（若有）解读三张牌，不要孤立讲牌义。
2. 尊重正逆位；牌阵为过去 / 现在 / 未来。
3. 若用户提出了具体问题，围绕该问题展开；否则做通用阶段解读。
4. 不装神棍，不承诺预测必然结果；语气具体、克制。
5. 全文简体中文，可用小标题：过去、现在、未来、综合。"""


def _client(api_key: str, base_url: Optional[str] = None) -> OpenAI:
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _chat(
    *,
    api_key: str,
    model: str,
    system: str,
    user: str,
    base_url: Optional[str] = None,
) -> str:
    client = _client(api_key, base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("LLM 返回空内容，请稍后重试。")
    return content.strip()


def build_main_user_prompt(chart: "ChartResult") -> str:
    parts = [
        "请根据以下星盘 ground truth 撰写解读报告。",
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


def generate_main_report(
    chart: "ChartResult",
    *,
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
) -> str:
    return _chat(
        api_key=api_key,
        model=model,
        system=MAIN_SYSTEM,
        user=build_main_user_prompt(chart),
        base_url=base_url,
    )


def generate_tarot_report(
    chart: "ChartResult",
    cards: list["DrawnCard"],
    *,
    question: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
) -> str:
    card_lines = "\n".join(f"- {c.label_zh()}" for c in cards)
    q = question.strip() or "（用户未提问，请做通用阶段解读）"
    mbti = chart.mbti or "不确定"
    user = "\n".join(
        [
            "请结合星盘与人格类型解读下列三张牌。",
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
    return _chat(
        api_key=api_key,
        model=model,
        system=TAROT_SYSTEM,
        user=user,
        base_url=base_url,
    )
