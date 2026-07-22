"""Shared visual tokens for the Streamlit app and exported reports."""

from __future__ import annotations


COLORS = {
    "bg": "#0b1626",
    "bg-deep": "#07101d",
    "surface": "#121f31",
    "surface-strong": "#18283d",
    "text": "#e7ddc9",
    "muted": "rgba(231, 221, 201, 0.68)",
    "accent": "#7fa79b",
    "accent-strong": "#a9c6bd",
    "coordinate": "#6e8fb4",
    "copper": "#a76d46",
    "line": "rgba(110, 143, 180, 0.24)",
    "border": "rgba(231, 221, 201, 0.20)",
    "glass": "rgba(18, 31, 49, 0.78)",
    "cta": "#c7d9d2",
    "cta-text": "#0b1626",
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
