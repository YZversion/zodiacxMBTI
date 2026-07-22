"""Build a downloadable Chinese PDF of the interpretation report."""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Optional, Sequence

from fpdf import FPDF

from chart import sign_to_zh
from design_system import BODY_FONT_STACK, DATA_FONT_STACK, DISPLAY_FONT_STACK, css_variables

PRIVACY = "出生信息仅用于本次计算，不存储、不留日志。"
DISCLAIMER = (
    "本报告由 AI 生成，内容仅供娱乐与自我探索，不构成心理、医疗或重大决策建议。"
)

QUESTION_SECTION_HEADING = "## 4. 关于你正在纠结的事"
_QUESTION_SECTION_RE = re.compile(
    r"(?ms)^\s*##\s*4(?:[.、．]|\s).*?(?=^\s*##\s+|\Z)"
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
    """Extract the closing one-line advice section (heading ## 5, legacy ## 4)."""
    if not report:
        return ""
    match = re.search(
        r"##\s*(?:5|4)[\.、．]?\s*当前阶段的一句话建议\s*\n+(.*?)(?=\n##\s|\Z)",
        report,
        flags=re.DOTALL,
    )
    if not match:
        return ""
    return match.group(1).strip()


def sanitize_main_report(report: str) -> str:
    """Normalize whitespace; keep §6 for collapsible rendering."""
    return (report or "").strip()


def has_complete_question_section(report: str) -> bool:
    """Return whether §4 exists and contains a substantive answer."""
    match = _QUESTION_SECTION_RE.search(report or "")
    if not match:
        return False
    lines = match.group(0).strip().splitlines()
    body = "\n".join(lines[1:]).strip()
    return len(re.sub(r"\s+", "", body)) >= 80


def upsert_question_section(report: str, section: str) -> str:
    """Normalize a generated §4 and place it before §5 without duplicates."""
    base = sanitize_main_report(report)
    addition = sanitize_main_report(section)
    if not addition:
        raise ValueError("针对用户问题的分析为空。")

    generated_match = _QUESTION_SECTION_RE.search(addition)
    if generated_match:
        addition = generated_match.group(0).strip()
    else:
        addition = f"{QUESTION_SECTION_HEADING}\n{addition}"

    existing_match = _QUESTION_SECTION_RE.search(base)
    if existing_match:
        before = base[: existing_match.start()].rstrip()
        after = base[existing_match.end() :].lstrip()
        return "\n\n".join(part for part in (before, addition, after) if part)

    next_section = re.search(
        r"(?m)^\s*##\s*(?:5|6)(?:[.、．]|\s)",
        base,
    )
    if next_section:
        before = base[: next_section.start()].rstrip()
        after = base[next_section.start() :].lstrip()
        return "\n\n".join(part for part in (before, addition, after) if part)
    return "\n\n".join(part for part in (base, addition) if part)


def split_extension_section(report: str) -> tuple[str, str]:
    """Split main body from ## 6 延伸/衍生探索. Returns (main, extension_body)."""
    if not report:
        return "", ""
    m = re.search(
        r"(?:\n|^)##\s*6[.、．]?\s*(?:延伸|衍生)探索\s*\n?(.*)\Z",
        report,
        flags=re.DOTALL,
    )
    if not m:
        return report.strip(), ""
    main = report[: m.start()].strip()
    return main, m.group(1).strip()


def parse_extension_items(extension_body: str) -> list[tuple[str, str]]:
    """Parse ### titled items, or legacy bullet teasers, into (title, body)."""
    body = (extension_body or "").strip()
    if not body:
        return []

    items: list[tuple[str, str]] = []
    # Preferred: ### Title + paragraphs
    chunks = re.split(r"(?m)^###\s+", body)
    if len(chunks) > 1:
        for chunk in chunks[1:]:
            lines = chunk.strip().splitlines()
            if not lines:
                continue
            title = re.sub(r"^#+\s*", "", lines[0]).strip()
            text = "\n".join(lines[1:]).strip()
            if title:
                items.append((title, text or "（暂无解析）"))
        if items:
            return items

    # Legacy: "- 想知道…吗？" bullets → fold each as title with placeholder body
    bullets = re.findall(r"(?m)^(?:[-*]|\d+[.、])\s*(.+)$", body)
    if bullets:
        for b in bullets:
            title = b.strip().rstrip("？?").lstrip("想知道").strip("，, ")
            if len(title) > 36:
                title = title[:36] + "…"
            items.append(
                (
                    title or "延伸探索",
                    "本条仍是旧版「只提问」格式。请重新生成报告，以获得带解析的折叠内容。",
                )
            )
        return items

    return [("延伸探索", body)]


def split_main_and_extensions(report: str) -> tuple[str, list[tuple[str, str]]]:
    main, ext = split_extension_section(report)
    return main, parse_extension_items(ext)


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


def _extensions_to_html(items: list[tuple[str, str]]) -> str:
    import html as html_lib

    if not items:
        return ""
    blocks: list[str] = []
    for title, body in items:
        body_html = _md_to_html(body) if body else "<p>（暂无解析）</p>"
        blocks.append(
            f'<details class="fold">'
            f"<summary>{html_lib.escape(title)}</summary>"
            f'<div class="fold-body prose">{body_html}</div>'
            f"</details>"
        )
    return (
        '<section class="section">'
        "<h1>延伸探索</h1>"
        '<p class="meta" style="margin-top:0">点开查看短解析</p>'
        + "".join(blocks)
        + "</section>"
    )


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

    design_tokens = css_variables()
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
          <details class="fold" open>
            <summary>塔罗补充 · 衍生探索</summary>
            <div class="fold-body">
              <div class="tarot-row">{''.join(cards_html)}</div>
              <div class="prose">{tarot_reading}</div>
            </div>
          </details>
        </section>
        """

    report_main, ext_items = split_main_and_extensions(report_text or "")
    report_html = _md_to_html(report_main)
    extension_block = _extensions_to_html(ext_items)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>星盘 × MBTI 性格解读</title>
<style>
  :root {{
    {design_tokens}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    color: var(--zx-text);
    font-family: {BODY_FONT_STACK};
    background:
      radial-gradient(circle at 78% 12%, rgba(110,143,180,0.18), transparent 26rem),
      linear-gradient(var(--zx-line) 1px, transparent 1px),
      linear-gradient(90deg, var(--zx-line) 1px, transparent 1px),
      linear-gradient(150deg, var(--zx-bg-deep) 0%, var(--zx-bg) 48%, #0e1b2d 100%);
    background-size: auto, 48px 48px, 48px 48px, auto;
    background-attachment: fixed;
    line-height: 1.65;
  }}
  .wrap {{
    max-width: 820px;
    margin: 0 auto;
    padding: 28px 18px 64px;
  }}
  .brand {{
    font-family: {DISPLAY_FONT_STACK};
    font-size: clamp(28px, 5vw, 40px);
    font-weight: 400;
    margin: 0 0 8px;
  }}
  .meta {{ color: var(--zx-muted); font-family: {DATA_FONT_STACK}; font-size: 12px; margin-bottom: 18px; }}
  .glass {{
    position: relative;
    background: var(--zx-glass);
    border: 1px solid var(--zx-border);
    border-radius: 16px;
    padding: 1.15rem 1.2rem;
    margin: 0 0 22px;
    backdrop-filter: blur(18px);
    box-shadow: 0 24px 60px rgba(2,8,16,0.42), inset 0 1px 0 rgba(231,221,201,0.10);
    overflow: hidden;
  }}
  .glass::before {{
    content: "";
    position: absolute; inset: 0; pointer-events: none;
    background:
      linear-gradient(135deg, rgba(231,221,201,0.09), transparent 40%),
      radial-gradient(circle at 86% 12%, rgba(127,167,155,0.20), transparent 32%);
  }}
  .headline {{
    position: relative;
    font-family: {DISPLAY_FONT_STACK};
    font-size: 1.45rem;
    line-height: 1.35;
    margin: 0 0 0.75rem;
  }}
  .advice-label {{
    position: relative;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--zx-muted);
    margin: 0 0 0.35rem;
  }}
  .advice {{ position: relative; margin: 0; font-size: 1.02rem; }}
  .note {{ color: var(--zx-accent-strong); font-size: 0.92rem; }}
  .section h1 {{
    font-family: {DISPLAY_FONT_STACK};
    font-size: 1.5rem;
    font-weight: 400;
    margin: 28px 0 12px;
  }}
  .chart-box {{
    width: min(520px, 100%);
    margin: 0 auto 8px;
    aspect-ratio: 1 / 1;
    background: var(--zx-surface);
    border-radius: 12px;
    border: 1px solid var(--zx-border);
    overflow: hidden;
  }}
  .chart-box svg {{ width: 100%; height: 100%; display: block; }}
  .prose h2 {{
    font-family: {DISPLAY_FONT_STACK};
    color: var(--zx-accent-strong);
    font-size: 1.15rem;
    font-weight: 400;
    margin: 1.2rem 0 0.45rem;
  }}
  .prose p {{ margin: 0.35rem 0; }}
  details.fold {{
    border: 1px solid var(--zx-border);
    border-radius: 12px;
    background: var(--zx-glass);
    padding: 0.4rem 1rem 1rem;
    margin: 1.25rem 0;
  }}
  details.fold > summary {{
    cursor: pointer;
    list-style: none;
    font-family: {DISPLAY_FONT_STACK};
    font-size: 1.35rem;
    color: var(--zx-accent-strong);
    padding: 0.75rem 0.15rem;
    user-select: none;
  }}
  details.fold > summary::-webkit-details-marker {{ display: none; }}
  details.fold > summary::after {{
    content: " ▾";
    font-size: 0.85em;
    opacity: 0.7;
  }}
  details.fold:not([open]) > summary::after {{ content: " ▸"; }}
  details.fold .fold-body {{ margin-top: 0.5rem; }}
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
  .tarot-card .pos {{ color: var(--zx-coordinate); font-family: {DATA_FONT_STACK}; font-size: 12px; margin-bottom: 6px; }}
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
  .badge-up {{ background: var(--zx-cta); color: var(--zx-cta-text); }}
  .badge-rev {{ background: #e3b9b0; color: #4f1814; }}
  .foot {{
    margin-top: 36px;
    color: var(--zx-muted);
    font-size: 12px;
    border-top: 1px solid var(--zx-border);
    padding-top: 14px;
  }}
  .print-hint {{
    margin: 0 0 18px;
    padding: 10px 12px;
    border: 1px dashed var(--zx-accent);
    border-radius: 10px;
    color: var(--zx-muted);
    font-size: 13px;
  }}
  @media print {{
    body {{ background: var(--zx-bg); -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
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
    {extension_block}
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
