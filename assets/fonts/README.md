# Fonts

**Noto Sans SC Regular** (`NotoSansSC-Regular.ttf`) — used by `report_export.py` for Chinese text PDFs.

**Noto Serif SC Medium** (`NotoSerifSC-Medium.ttf`) — source for the offline persona-card compositor (`tools/build_cards.py`).

**Subsets** (committed for Cloud / reproducible builds):

- `NotoSansSC-Regular.subset.ttf`
- `NotoSerifSC-Medium.subset.ttf`

Rebuild with:

```bash
python tools/build_cards.py --subset-fonts
```

The compositor refuses to run without these files (no DejaVu fallback).

- License: [SIL Open Font License 1.1](https://scripts.sil.org/OFL)
- Sans source: [Google Fonts — Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)
- Serif source: [Google Fonts — Noto Serif SC](https://fonts.google.com/noto/specimen/Noto+Serif+SC) (Medium / weight 500)

UI web fonts (Instrument Serif, Space Grotesk, Noto Sans/Serif SC) are loaded from Google Fonts at runtime in `app.py` theme CSS — not stored here.
