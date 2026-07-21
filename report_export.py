"""Build a downloadable Chinese PDF of the interpretation report."""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Optional, Sequence

from fpdf import FPDF

from chart import sign_to_zh

PRIVACY = "出生信息仅用于本次计算，不存储、不留日志。"
DISCLAIMER = (
    "本报告由 AI 生成，内容仅供娱乐与自我探索，不构成心理、医疗或重大决策建议。"
)

FONT_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "fonts" / "NotoSansSC-Regular.ttf",
    Path(r"C:\Windows\Fonts\NotoSansSC-Regular.ttf"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/System/Library/Fonts/PingFang.ttc"),
]


class FontNotFoundError(RuntimeError):
    pass


def resolve_cjk_font() -> Path:
    for path in FONT_CANDIDATES:
        if path.is_file():
            return path
    raise FontNotFoundError(
        "未找到中文字体。请将 NotoSansSC-Regular.ttf 放到 assets/fonts/ 后重试。"
    )


def extract_section_4_advice(report: str) -> str:
    if not report:
        return ""
    match = re.search(
        r"##\s*4[\.、．]?\s*当前阶段的一句话建议\s*\n+(.*?)(?=\n##\s|\Z)",
        report,
        flags=re.DOTALL,
    )
    if not match:
        return ""
    return match.group(1).strip()


def summary_headline(chart) -> str:
    sun = sign_to_zh(chart.sun_sign)
    parts = [f"太阳{sun}座"]
    if chart.moon_ambiguity:
        a = sign_to_zh(chart.moon_ambiguity.sign_at_start)
        b = sign_to_zh(chart.moon_ambiguity.sign_at_end)
        parts.append(f"月亮{a}/{b}座?")
    else:
        parts.append(f"月亮{sign_to_zh(chart.moon_sign)}座")
    if not chart.time_unknown and chart.asc_sign:
        parts.append(f"上升{sign_to_zh(chart.asc_sign)}座")
    line = " · ".join(parts)
    mbti = chart.mbti or "未定"
    return f"{line} × {mbti}"


def _clean_md(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        if not line.strip():
            blocks.append(("blank", ""))
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line.strip())
        if m:
            blocks.append(("title", m.group(2).strip()))
        else:
            plain = re.sub(r"[*_`]+", "", line)
            blocks.append(("body", plain))
    return blocks


class _ReportPDF(FPDF):
    def __init__(self, font_path: Path):
        super().__init__(format="A4", unit="mm")
        self.set_auto_page_break(auto=True, margin=18)
        self.add_font("ReportCJK", fname=str(font_path))
        self.set_font("ReportCJK", size=11)

    def footer(self) -> None:
        self.set_y(-16)
        self.set_font("ReportCJK", size=8)
        self.set_text_color(110, 110, 110)
        self.multi_cell(0, 4, DISCLAIMER, align="C", new_x="LMARGIN", new_y="NEXT")


def _write(pdf: FPDF, text: str, *, h: float = 6.5) -> None:
    pdf.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")


def _md_to_html(text: str) -> str:
    import html as html_lib

    parts: list[str] = []
    for kind, line in _clean_md(text or ""):
        if kind == "blank":
            parts.append("<br />")
        elif kind == "title":
            parts.append(f"<h2>{html_lib.escape(line)}</h2>")
        else:
            parts.append(f"<p>{html_lib.escape(line)}</p>")
    return "\n".join(parts)


def build_report_html(
    *,
    chart,
    report_text: str,
    tarot_cards: Optional[Sequence] = None,
    tarot_text: Optional[str] = None,
) -> str:
    """Self-contained dark-page snapshot: summary + chart SVG + tarot art + report."""
    import html as html_lib

    from tarot_ui import card_face_data_uri

    headline = html_lib.escape(summary_headline(chart))
    advice = extract_section_4_advice(report_text or "")
    advice_html = (
        f'<p class="advice-label">当前阶段的一句话建议</p>'
        f'<p class="advice">{html_lib.escape(advice)}</p>'
        if advice
        else ""
    )

    meta_bits = [
        f"地点：{chart.resolved_city or chart.city}（{chart.nation}）",
    ]
    if chart.resolved_tz:
        meta_bits.append(f"时区：{chart.resolved_tz}")
    if chart.time_unknown:
        meta_bits.append("出生时间：未知（已降级）")
    elif chart.birth_time:
        meta_bits.append(
            f"出生：{chart.birth_date.isoformat()} {chart.birth_time.strftime('%H:%M')}"
        )
    else:
        meta_bits.append(f"出生日期：{chart.birth_date.isoformat()}")
    if chart.mbti:
        meta_bits.append(f"MBTI：{chart.mbti}")
    meta = html_lib.escape(" · ".join(meta_bits))

    notes_html = "".join(
        f'<p class="note">※ {html_lib.escape(n)}</p>' for n in (chart.preface_notes or [])
    )

    # Chart SVG is trusted app output; strip scripts just in case
    chart_svg = re.sub(
        r"<script\b[^>]*>.*?</script>",
        "",
        chart.svg or "",
        flags=re.IGNORECASE | re.DOTALL,
    )

    tarot_block = ""
    if tarot_cards:
        cards_html: list[str] = []
        for card in tarot_cards:
            try:
                uri = card_face_data_uri(card.name)
            except KeyError:
                uri = ""
            orient = "逆位" if card.reversed else "正位"
            rev_cls = " reversed" if card.reversed else ""
            badge_cls = "badge-rev" if card.reversed else "badge-up"
            img = (
                f'<img class="card-img{rev_cls}" src="{uri}" alt="{html_lib.escape(card.name)}" />'
                if uri
                else ""
            )
            cards_html.append(
                f"""
                <div class="tarot-card">
                  <div class="pos">{html_lib.escape(card.position)}</div>
                  {img}
                  <div class="name">{html_lib.escape(card.name)}</div>
                  <span class="badge {badge_cls}">{orient}</span>
                </div>
                """
            )
        tarot_reading = _md_to_html(tarot_text or "")
        tarot_block = f"""
        <section class="section">
          <h1>塔罗补充</h1>
          <div class="tarot-row">{''.join(cards_html)}</div>
          <div class="prose">{tarot_reading}</div>
        </section>
        """

    report_html = _md_to_html(report_text or "")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>星盘 × MBTI 性格解读</title>
<style>
  :root {{
    --bg: #05060a;
    --text: #f4f1ea;
    --muted: rgba(244,241,234,0.62);
    --glass: rgba(255,255,255,0.08);
    --border: rgba(255,255,255,0.22);
    --accent: #c9a46c;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    color: var(--text);
    font-family: "Space Grotesk", "Noto Sans SC", "Microsoft YaHei", sans-serif;
    background:
      radial-gradient(1.4px 1.4px at 8% 12%, rgba(255,255,255,0.55) 0, transparent 2px),
      radial-gradient(1px 1px at 46% 68%, rgba(255,255,255,0.28) 0, transparent 2px),
      radial-gradient(1.3px 1.3px at 78% 24%, rgba(201,164,108,0.4) 0, transparent 2px),
      radial-gradient(1px 1px at 22% 82%, rgba(255,255,255,0.35) 0, transparent 2px),
      linear-gradient(165deg, #05060a 0%, #0a0d16 45%, #07080f 100%);
    background-attachment: fixed;
    line-height: 1.65;
  }}
  .wrap {{
    max-width: 820px;
    margin: 0 auto;
    padding: 28px 18px 64px;
  }}
  .brand {{
    font-family: "Instrument Serif", "Noto Serif SC", Georgia, serif;
    font-size: clamp(28px, 5vw, 40px);
    font-weight: 400;
    margin: 0 0 8px;
  }}
  .meta {{ color: var(--muted); font-size: 13px; margin-bottom: 18px; }}
  .glass {{
    position: relative;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.15rem 1.2rem;
    margin: 0 0 22px;
    backdrop-filter: blur(18px);
    box-shadow: 0 24px 60px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.14);
    overflow: hidden;
  }}
  .glass::before {{
    content: "";
    position: absolute; inset: 0; pointer-events: none;
    background:
      linear-gradient(135deg, rgba(255,255,255,0.14), transparent 40%),
      radial-gradient(circle at 86% 12%, rgba(201,164,108,0.18), transparent 32%);
  }}
  .headline {{
    position: relative;
    font-family: "Instrument Serif", "Noto Serif SC", Georgia, serif;
    font-size: 1.45rem;
    line-height: 1.35;
    margin: 0 0 0.75rem;
  }}
  .advice-label {{
    position: relative;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 0.35rem;
  }}
  .advice {{ position: relative; margin: 0; font-size: 1.02rem; }}
  .note {{ color: #e2c48a; font-size: 0.92rem; }}
  .section h1 {{
    font-family: "Instrument Serif", "Noto Serif SC", Georgia, serif;
    font-size: 1.5rem;
    font-weight: 400;
    margin: 28px 0 12px;
  }}
  .chart-box {{
    width: min(520px, 100%);
    margin: 0 auto 8px;
    aspect-ratio: 1 / 1;
    background: #0a0d16;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.12);
    overflow: hidden;
  }}
  .chart-box svg {{ width: 100%; height: 100%; display: block; }}
  .prose h2 {{
    font-family: "Instrument Serif", "Noto Serif SC", Georgia, serif;
    color: var(--accent);
    font-size: 1.15rem;
    font-weight: 400;
    margin: 1.2rem 0 0.45rem;
  }}
  .prose p {{ margin: 0.35rem 0; }}
  .tarot-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    justify-content: center;
    margin: 10px 0 18px;
  }}
  .tarot-card {{
    width: 148px;
    text-align: center;
  }}
  .tarot-card .pos {{ color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
  .tarot-card .name {{ font-size: 14px; font-weight: 600; margin: 8px 0 6px; }}
  .card-img {{
    width: 100%;
    border-radius: 10px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.4);
    display: block;
  }}
  .card-img.reversed {{ transform: rotate(180deg); }}
  .badge {{
    display: inline-block;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 999px;
    font-weight: 600;
  }}
  .badge-up {{ background: #dceee3; color: #1f6b45; }}
  .badge-rev {{ background: #f3d9d4; color: #8a2f2a; }}
  .foot {{
    margin-top: 36px;
    color: var(--muted);
    font-size: 12px;
    border-top: 1px solid rgba(255,255,255,0.12);
    padding-top: 14px;
  }}
  .print-hint {{
    margin: 0 0 18px;
    padding: 10px 12px;
    border: 1px dashed rgba(201,164,108,0.45);
    border-radius: 10px;
    color: var(--muted);
    font-size: 13px;
  }}
  @media print {{
    body {{ background: #05060a; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .print-hint {{ display: none; }}
    .wrap {{ padding: 0; max-width: 100%; }}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <p class="print-hint">这是完整页面快照。若需要 PDF：用浏览器打开本文件 → 打印 → 另存为 PDF。</p>
    <h1 class="brand">星盘 × MBTI 性格解读</h1>
    <p class="meta">{meta}</p>
    <div class="glass">
      <p class="headline">{headline}</p>
      {advice_html}
    </div>
    {notes_html}
    <section class="section">
      <h1>本命盘</h1>
      <div class="chart-box">{chart_svg}</div>
    </section>
    <section class="section">
      <h1>解读报告</h1>
      <div class="prose">{report_html}</div>
    </section>
    {tarot_block}
    <div class="foot">
      <p>{html_lib.escape(PRIVACY)}</p>
      <p>{html_lib.escape(DISCLAIMER)}</p>
    </div>
  </div>
</body>
</html>
"""


def build_report_pdf(
    *,
    chart,
    report_text: str,
    tarot_cards: Optional[Sequence] = None,
    tarot_text: Optional[str] = None,
) -> bytes:
    font_path = resolve_cjk_font()
    pdf = _ReportPDF(font_path)
    pdf.add_page()
    pdf.set_text_color(28, 27, 25)

    pdf.set_font("ReportCJK", size=18)
    _write(pdf, "星盘 × MBTI 性格解读", h=10)
    pdf.ln(2)

    pdf.set_font("ReportCJK", size=13)
    pdf.set_text_color(44, 74, 110)
    _write(pdf, summary_headline(chart), h=8)
    pdf.set_text_color(28, 27, 25)
    pdf.ln(1)

    advice = extract_section_4_advice(report_text or "")
    if advice:
        pdf.set_font("ReportCJK", size=10)
        pdf.set_text_color(107, 101, 92)
        _write(pdf, "当前阶段的一句话建议", h=6)
        pdf.set_text_color(28, 27, 25)
        pdf.set_font("ReportCJK", size=11)
        _write(pdf, advice, h=7)
        pdf.ln(2)

    meta_bits = [
        f"地点：{chart.resolved_city or chart.city}（{chart.nation}）",
    ]
    if chart.resolved_tz:
        meta_bits.append(f"时区：{chart.resolved_tz}")
    if chart.time_unknown:
        meta_bits.append("出生时间：未知（已降级）")
    elif chart.birth_time:
        meta_bits.append(
            f"出生：{chart.birth_date.isoformat()} {chart.birth_time.strftime('%H:%M')}"
        )
    else:
        meta_bits.append(f"出生日期：{chart.birth_date.isoformat()}")
    if chart.mbti:
        meta_bits.append(f"MBTI：{chart.mbti}")

    pdf.set_font("ReportCJK", size=9)
    pdf.set_text_color(107, 101, 92)
    _write(pdf, " · ".join(meta_bits), h=5)
    pdf.set_text_color(28, 27, 25)
    pdf.ln(2)

    for note in chart.preface_notes or []:
        pdf.set_font("ReportCJK", size=10)
        pdf.set_text_color(90, 70, 40)
        _write(pdf, f"※ {note}", h=6)
        pdf.set_text_color(28, 27, 25)
    if chart.preface_notes:
        pdf.ln(1)

    pdf.set_font("ReportCJK", size=14)
    _write(pdf, "解读报告", h=8)
    pdf.ln(1)

    for kind, line in _clean_md(report_text or ""):
        if kind == "blank":
            pdf.ln(3)
        elif kind == "title":
            pdf.ln(2)
            pdf.set_font("ReportCJK", size=12)
            pdf.set_text_color(44, 74, 110)
            _write(pdf, line, h=7)
            pdf.set_text_color(28, 27, 25)
            pdf.set_font("ReportCJK", size=11)
        else:
            pdf.set_font("ReportCJK", size=11)
            _write(pdf, line, h=6.5)

    if tarot_cards:
        pdf.add_page()
        pdf.set_font("ReportCJK", size=14)
        _write(pdf, "塔罗补充（过去 / 现在 / 未来）", h=8)
        pdf.ln(2)
        pdf.set_font("ReportCJK", size=11)
        for card in tarot_cards:
            _write(pdf, f"· {card.label_zh()}", h=7)
        pdf.ln(2)
        if tarot_text:
            for kind, line in _clean_md(tarot_text):
                if kind == "blank":
                    pdf.ln(3)
                elif kind == "title":
                    pdf.ln(2)
                    pdf.set_font("ReportCJK", size=12)
                    pdf.set_text_color(44, 74, 110)
                    _write(pdf, line, h=7)
                    pdf.set_text_color(28, 27, 25)
                    pdf.set_font("ReportCJK", size=11)
                else:
                    pdf.set_font("ReportCJK", size=11)
                    _write(pdf, line, h=6.5)

    pdf.ln(6)
    pdf.set_font("ReportCJK", size=8)
    pdf.set_text_color(107, 101, 92)
    _write(pdf, PRIVACY, h=4)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
