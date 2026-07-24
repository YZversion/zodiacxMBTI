"""Shared visual tokens for the Streamlit app and exported reports."""

from __future__ import annotations


COLORS = {
    "bg": "#09131f",
    "bg-deep": "#050b12",
    "surface": "#101d2b",
    "surface-strong": "#182a3c",
    "text": "#eee5d4",
    "muted": "rgba(238, 229, 212, 0.68)",
    "accent": "#a96048",
    "accent-strong": "#c7af85",
    "coordinate": "#94aabd",
    "copper": "#b66f50",
    "line": "rgba(199, 175, 133, 0.20)",
    "border": "rgba(199, 175, 133, 0.34)",
    "glass": "rgba(10, 21, 34, 0.84)",
    "cta": "#c7af85",
    "cta-text": "#09131f",
    "danger": "#c66a5a",
}

DISPLAY_FONT_STACK = (
    '"Kaiti SC", "STKaiti", "KaiTi", "Noto Serif SC", Georgia, serif'
)
BODY_FONT_STACK = (
    '"Noto Sans SC", "Microsoft YaHei", "PingFang SC", system-ui, sans-serif'
)
DATA_FONT_STACK = (
    '"Space Grotesk", "Cascadia Code", "SFMono-Regular", Consolas, monospace'
)


def css_variables(prefix: str = "zx") -> str:
    """Return one shared CSS custom-property block body."""
    color_lines = [f"--{prefix}-{name}: {value};" for name, value in COLORS.items()]
    font_lines = [
        f"--{prefix}-display: {DISPLAY_FONT_STACK};",
        f"--{prefix}-body: {BODY_FONT_STACK};",
        f"--{prefix}-data: {DATA_FONT_STACK};",
    ]
    return "\n  ".join(color_lines + font_lines)
