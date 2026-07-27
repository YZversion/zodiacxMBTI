"""Offline compositor: persona art + JSON -> shareable 1080x1440 WebP cards."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "persona_cards" / "persona_cards.json"
ART_ROOT = ROOT / "personapicture" / "mbti_tarot_cards"
OUT_WEBP = ROOT / "assets" / "cards" / "webp"
OUT_PNG = ROOT / "assets" / "cards" / "png"
MANIFEST_PATH = ROOT / "assets" / "cards" / "manifest.json"
CONTACT_DIR = ROOT / "build" / "contact_sheets"
FONT_SANS_SRC = ROOT / "assets" / "fonts" / "NotoSansSC-Regular.ttf"
FONT_SERIF_SRC = ROOT / "assets" / "fonts" / "NotoSerifSC-Medium.ttf"
FONT_SANS_SUBSET = ROOT / "assets" / "fonts" / "NotoSansSC-Regular.subset.ttf"
FONT_SERIF_SUBSET = ROOT / "assets" / "fonts" / "NotoSerifSC-Medium.subset.ttf"

APP_URL = "https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app"

SIGNS_ORDER: tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

MBTI_ORDER: tuple[str, ...] = (
    "ISTJ",
    "ISFJ",
    "INFJ",
    "INTJ",
    "ISTP",
    "ISFP",
    "INFP",
    "INTP",
    "ESTP",
    "ESFP",
    "ENFP",
    "ENTP",
    "ESTJ",
    "ESFJ",
    "ENFJ",
    "ENTJ",
)

SIGN_COLORS: dict[str, tuple[str, str]] = {
    "Aries": ("#1A0E0B", "#A8502E"),
    "Taurus": ("#0D1410", "#8A7434"),
    "Gemini": ("#0C1216", "#6E8A96"),
    "Cancer": ("#0B1016", "#6B7E96"),
    "Leo": ("#150F06", "#B08A32"),
    "Virgo": ("#0F1210", "#7E8C7A"),
    "Libra": ("#151011", "#A8836E"),
    "Scorpio": ("#100608", "#8A2E36"),
    "Sagittarius": ("#160E08", "#A87038"),
    "Capricorn": ("#0B0E12", "#6A7482"),
    "Aquarius": ("#0A0D16", "#5C6A9A"),
    "Pisces": ("#0A1214", "#5E8A8A"),
}

TEXT_PRIMARY = "#E8DCC4"
TEXT_SECONDARY = "#A89878"
QR_FG = "#A89878"

ART_NAME_RE = re.compile(
    r"^(?P<nn>\d{2})_(?P<mbti>[A-Z]{4})_(?P<sign>[A-Za-z]+)_(?P<tag>\w+)\.png$"
)


@dataclass(frozen=True)
class Layout:
    width: int = 1080
    height: int = 1440
    art_box_w: int = 700
    art_box_h: int = 1150
    art_top: int = 70
    divider_y: int = 1254
    text_pad_x: int = 80
    nickname_y: int = 1258
    nickname_size: int = 48
    nickname_tracking: float = 0.05
    pct_size: int = 30
    pct_right_x: int = 1000
    index_y: int = 1302
    index_size: int = 20
    paradox_y: int = 1332
    paradox_size: int = 28
    paradox_max_w: int = 804
    combo_y: int = 1388
    combo_size: int = 22
    qr_size: int = 92
    qr_x: int = 908
    qr_y: int = 1306
    qr_pad: int = 8


LAYOUT = Layout()


def rarity_from_pct(pct: float) -> str:
    if pct <= 0.15:
        return "最稀有"
    if pct <= 0.25:
        return "稀有"
    if pct <= 0.40:
        return "少见"
    if pct <= 0.70:
        return "较为常见"
    return "常见"


def text_units(s: str) -> float:
    return sum(1.0 if ord(ch) > 127 else 0.5 for ch in s)


def strip_paradox_end(s: str) -> str:
    return s.rstrip().rstrip("。！!?？")


def card_index(mbti: str, sun_en: str) -> int:
    si = SIGNS_ORDER.index(sun_en)
    mi = MBTI_ORDER.index(mbti)
    return si * 16 + mi + 1


def format_pct(pct: float) -> str:
    s = f"{pct:.2f}"
    if s.endswith("0"):
        s = s[:-1]
    return s


def pct_line_for(mbti: str, pct: float, label: str) -> str:
    return f"人口占比 ≈ {format_pct(pct)}%（{mbti}÷12 · {label}）"


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def load_cards_json() -> dict[str, Any]:
    return json.loads(CARDS_PATH.read_text(encoding="utf-8"))


def save_cards_json(data: dict[str, Any]) -> None:
    CARDS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def layout_fingerprint() -> str:
    raw = repr(LAYOUT)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def build_fingerprint() -> str:
    import PIL
    import qrcode
    from fontTools import __version__ as ft_ver

    return (
        f"Pillow={PIL.__version__} qrcode={getattr(qrcode, '__version__', '?')} "
        f"fonttools={ft_ver} layout={layout_fingerprint()}"
    )


def discover_art(sign_en: str) -> dict[str, Path]:
    folder = ART_ROOT / sign_en.lower() / "v1"
    if not folder.is_dir():
        return {}
    found: dict[str, Path] = {}
    for path in sorted(folder.glob("*.png")):
        m = ART_NAME_RE.match(path.name)
        if not m:
            print(f"SKIP unparsable art: {path}")
            continue
        mbti = m.group("mbti")
        sign = m.group("sign")
        if sign != sign_en:
            print(f"SKIP sign mismatch: {path.name}")
            continue
        cid = f"{mbti}_{sign_en}"
        if cid in found:
            print(f"WARN duplicate art for {cid}: {path.name}")
            continue
        found[cid] = path
    return found


def require_fonts(*, prefer_subset: bool = True) -> tuple[Path, Path]:
    sans = FONT_SANS_SUBSET if prefer_subset and FONT_SANS_SUBSET.is_file() else FONT_SANS_SRC
    serif = FONT_SERIF_SUBSET if prefer_subset and FONT_SERIF_SUBSET.is_file() else FONT_SERIF_SRC
    missing = [p for p in (sans, serif) if not p.is_file()]
    if missing:
        for p in missing:
            print(f"ERROR missing font: {p}")
        sys.exit(1)
    return sans, serif


def collect_subset_text(data: dict[str, Any]) -> str:
    chars: set[str] = set(" ≈%№/0123456789.×·（）()_-—,，、：:;！!?？“”\"'")
    chars.update("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for row in data.get("cards", []):
        for key in ("nickname", "paradox", "sun_zh", "mbti"):
            chars.update(row.get(key, ""))
    for sign in SIGNS_ORDER:
        chars.update(sign)
    return "".join(sorted(chars))


def subset_fonts(data: dict[str, Any]) -> None:
    from fontTools.subset import main as subset_main

    require_fonts(prefer_subset=False)
    text = collect_subset_text(data)
    text_file = ROOT / "build" / "_subset_chars.txt"
    text_file.parent.mkdir(parents=True, exist_ok=True)
    text_file.write_text(text, encoding="utf-8")

    for src, dst in (
        (FONT_SANS_SRC, FONT_SANS_SUBSET),
        (FONT_SERIF_SRC, FONT_SERIF_SUBSET),
    ):
        args = [
            str(src),
            f"--text-file={text_file}",
            "--no-layout-closure",
            f"--output-file={dst}",
            "--glyph-names",
            "--legacy-kern",
            "--name-IDs=*",
            "--name-legacy",
            "--name-languages=*",
        ]
        print(f"subset {src.name} -> {dst.name} ({len(text)} chars)")
        subset_main(args)
        if not dst.is_file():
            print(f"ERROR subset failed: {dst}")
            sys.exit(1)


def cmd_normalize() -> int:
    data = load_cards_json()
    diffs: list[str] = []
    paradox_long: list[str] = []
    def_warn: list[str] = []
    rarity_labels: dict[str, str] = {}

    for row in data.get("cards", []):
        cid = row["id"]
        mbti = row["mbti"]
        pct = float(row["pct"])
        new_label = rarity_from_pct(pct)
        old_label = row.get("rarity_label", "")
        if old_label != new_label:
            diffs.append(f"{cid}: rarity_label {old_label!r} -> {new_label!r}")
        row["rarity_label"] = new_label
        rarity_labels[mbti] = new_label

        old_paradox = row["paradox"]
        new_paradox = strip_paradox_end(old_paradox)
        if new_paradox != old_paradox:
            diffs.append(f"{cid}: paradox strip {old_paradox!r} -> {new_paradox!r}")
        row["paradox"] = new_paradox
        u = text_units(new_paradox)
        if u > 24:
            paradox_long.append(f"{cid}\t{u}\t{new_paradox}")

        defn = row.get("definition", "")
        if len(defn) > 26:
            def_warn.append(f"{cid}\t{len(defn)}\t{defn}")

        new_line = pct_line_for(mbti, pct, new_label)
        if row.get("pct_line") != new_line:
            diffs.append(f"{cid}: pct_line -> {new_line}")
        row["pct_line"] = new_line

    data["rarity_labels"] = {m: rarity_labels.get(m, data.get("rarity_labels", {}).get(m, "")) for m in MBTI_ORDER}
    # fill from cards for any missing
    for row in data["cards"]:
        data["rarity_labels"][row["mbti"]] = row["rarity_label"]

    print(f"=== normalize diff ({len(diffs)} lines) ===")
    for line in diffs:
        print(line)
    print(f"=== definition warnings (>26 chars): {len(def_warn)} ===")
    for line in def_warn:
        print(line)
    print(f"=== paradox too long (>24): {len(paradox_long)} ===")
    for line in paradox_long:
        print(line)

    if paradox_long:
        print("ERROR: fix paradoxes manually, then re-run --normalize")
        return 1

    save_cards_json(data)
    print(f"Wrote {CARDS_PATH}")
    print(build_fingerprint())
    return 0


def cmd_check(*, sign: Optional[str]) -> int:
    print(build_fingerprint())
    data = load_cards_json()
    cards = data.get("cards", [])
    errors: list[str] = []

    ids = [c["id"] for c in cards]
    if len(ids) != 192:
        errors.append(f"expected 192 cards, got {len(ids)}")
    if len(set(ids)) != len(ids):
        errors.append("duplicate card ids in JSON")

    expected = {f"{m}_{s}" for s in SIGNS_ORDER for m in MBTI_ORDER}
    got = set(ids)
    missing = sorted(expected - got)
    extra = sorted(got - expected)
    if missing:
        errors.append(f"JSON missing ids: {missing[:8]}...")
    if extra:
        errors.append(f"JSON unexpected ids: {extra[:8]}...")

    pairs = [(c["mbti"], c["sun_en"]) for c in cards]
    if len(set(pairs)) != len(pairs):
        errors.append("duplicate (mbti, sun_en) pairs")

    for c in cards:
        label = rarity_from_pct(float(c["pct"]))
        if c.get("rarity_label") != label:
            errors.append(f"{c['id']}: rarity_label {c.get('rarity_label')!r} != {label!r}")
        u = text_units(c.get("paradox", ""))
        if u > 24:
            errors.append(f"{c['id']}: paradox units {u} > 24")

    signs_to_check: list[str]
    if sign:
        signs_to_check = [sign]
    else:
        signs_to_check = list(SIGNS_ORDER)

    for sun in signs_to_check:
        art = discover_art(sun)
        folder = ART_ROOT / sun.lower() / "v1"
        if not folder.is_dir():
            if sign:
                errors.append(f"{sun}: art directory missing: {folder}")
            # C strategy: whole sign missing is OK when scanning all
            continue
        if not art and not sign:
            continue
        expected_ids = {f"{m}_{sun}" for m in MBTI_ORDER}
        missing_art = sorted(expected_ids - set(art))
        extra_art = sorted(set(art) - expected_ids)
        if missing_art:
            errors.append(f"{sun}: missing art for {missing_art}")
        if extra_art:
            errors.append(f"{sun}: unexpected art ids {extra_art}")
        if len(art) not in (0, 16) and folder.is_dir():
            # partial set
            if 0 < len(art) < 16:
                errors.append(f"{sun}: partial art set {len(art)}/16")

        from PIL import Image

        for cid, path in art.items():
            with Image.open(path) as im:
                ratio = im.width / im.height
                if not (0.55 <= ratio <= 0.68):
                    errors.append(
                        f"{cid}: aspect {ratio:.3f} outside 0.55–0.68 ({im.width}x{im.height})"
                    )

    if errors:
        print(f"=== check FAILED ({len(errors)}) ===")
        for e in errors:
            print(e)
        return 1
    print("=== check OK ===")
    return 0


def cmd_sample_colors() -> int:
    from PIL import Image
    import statistics

    for sun in SIGNS_ORDER:
        art = discover_art(sun)
        if not art:
            print(f"{sun}: (no art)")
            continue
        # sample first available
        path = next(iter(art.values()))
        with Image.open(path) as im:
            rgb = im.convert("RGB")
            w, h = rgb.size
            patches = [
                rgb.crop((0, 0, 16, 16)),
                rgb.crop((w - 16, 0, w, 16)),
                rgb.crop((0, h - 16, 16, h)),
                rgb.crop((w - 16, h - 16, w, h)),
            ]
            channels: list[list[int]] = [[], [], []]
            for patch in patches:
                for px in patch.getdata():
                    for i in range(3):
                        channels[i].append(int(px[i]))
            med = tuple(int(statistics.median(ch)) for ch in channels)
            suggested = f"#{med[0]:02X}{med[1]:02X}{med[2]:02X}"
            current = SIGN_COLORS[sun][0]
            print(f"{sun}: suggested_mat={suggested} current={current} sample={path.name}")
    return 0


def make_qr(mat_hex: str) -> "Image.Image":
    import qrcode
    from PIL import Image

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=0,
    )
    qr.add_data(APP_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color=QR_FG, back_color=mat_hex).convert("RGB")
    pad = LAYOUT.qr_pad
    canvas = Image.new("RGB", (img.width + pad * 2, img.height + pad * 2), hex_to_rgb(mat_hex))
    canvas.paste(img, (pad, pad))
    return canvas.resize((LAYOUT.qr_size, LAYOUT.qr_size), Image.Resampling.NEAREST)


def draw_tracked_text(
    draw: Any,
    xy: tuple[int, int],
    text: str,
    font: Any,
    fill: str,
    tracking_em: float,
) -> None:
    x, y = xy
    # approximate em from font size
    size = getattr(font, "size", LAYOUT.nickname_size)
    gap = tracking_em * size
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        bbox = draw.textbbox((x, y), ch, font=font)
        x = bbox[2] + gap


def compose_one(
    row: dict[str, Any],
    art_path: Path,
    *,
    sans_path: Path,
    serif_path: Path,
) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    sun = row["sun_en"]
    mat, accent = SIGN_COLORS[sun]
    L = LAYOUT
    canvas = Image.new("RGB", (L.width, L.height), hex_to_rgb(mat))

    art = Image.open(art_path).convert("RGBA")
    scale = min(L.art_box_w / art.width, L.art_box_h / art.height)
    new_w = max(1, int(round(art.width * scale)))
    new_h = max(1, int(round(art.height * scale)))
    art_r = art.resize((new_w, new_h), Image.Resampling.LANCZOS)
    art_x = (L.width - new_w) // 2
    art_y = L.art_top
    canvas.paste(art_r, (art_x, art_y), art_r)

    draw = ImageDraw.Draw(canvas, "RGBA")
    accent_rgba = (*hex_to_rgb(accent), int(255 * 0.6))
    div_x0 = art_x
    div_x1 = art_x + new_w - 1
    draw.line([(div_x0, L.divider_y), (div_x1, L.divider_y)], fill=accent_rgba, width=1)

    serif = ImageFont.truetype(str(serif_path), L.nickname_size)
    sans_pct = ImageFont.truetype(str(sans_path), L.pct_size)
    sans_idx = ImageFont.truetype(str(sans_path), L.index_size)
    sans_par = ImageFont.truetype(str(sans_path), L.paradox_size)
    sans_combo = ImageFont.truetype(str(sans_path), L.combo_size)

    nickname = row["nickname"]
    draw_tracked_text(
        draw,
        (L.text_pad_x, L.nickname_y),
        nickname,
        serif,
        TEXT_PRIMARY,
        L.nickname_tracking,
    )

    pct = float(row["pct"])
    pct_text = f"≈ {format_pct(pct)}%"
    pct_bbox = draw.textbbox((0, 0), pct_text, font=sans_pct)
    pct_w = pct_bbox[2] - pct_bbox[0]
    draw.text((L.pct_right_x - pct_w, L.nickname_y), pct_text, font=sans_pct, fill=TEXT_SECONDARY)

    idx = card_index(row["mbti"], sun)
    idx_text = f"№ {idx} / 192"
    idx_bbox = draw.textbbox((0, 0), idx_text, font=sans_idx)
    idx_w = idx_bbox[2] - idx_bbox[0]
    draw.text((L.pct_right_x - idx_w, L.index_y), idx_text, font=sans_idx, fill=TEXT_SECONDARY)

    paradox = row["paradox"]
    par_bbox = draw.textbbox((0, 0), paradox, font=sans_par)
    par_w = par_bbox[2] - par_bbox[0]
    if par_w > L.paradox_max_w:
        raise RuntimeError(f"{row['id']}: paradox width {par_w} > {L.paradox_max_w}")
    draw.text((L.text_pad_x, L.paradox_y), paradox, font=sans_par, fill=TEXT_PRIMARY)

    combo = f"{row['sun_zh']} × {row['mbti']}"
    draw.text((L.text_pad_x, L.combo_y), combo, font=sans_combo, fill=TEXT_SECONDARY)

    qr = make_qr(mat)
    canvas.paste(qr, (L.qr_x, L.qr_y))

    OUT_PNG.mkdir(parents=True, exist_ok=True)
    OUT_WEBP.mkdir(parents=True, exist_ok=True)
    png_path = OUT_PNG / f"{row['id']}.png"
    webp_path = OUT_WEBP / f"{row['id']}.webp"
    rgb = canvas.convert("RGB")
    rgb.save(png_path, format="PNG", optimize=True)
    rgb.save(webp_path, format="WEBP", quality=82, method=6)
    return webp_path


def merge_manifest(entries: dict[str, dict[str, Any]]) -> None:
    if MANIFEST_PATH.is_file():
        raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "cards" in raw:
            existing = {c["id"]: c for c in raw["cards"]}
        elif isinstance(raw, dict):
            existing = dict(raw)
        else:
            existing = {}
    else:
        existing = {}
    existing.update(entries)
    ordered = sorted(existing.values(), key=lambda c: int(c.get("index", 0)))
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "cards": ordered}
    MANIFEST_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def contact_sheet(sun: str, webps: list[tuple[int, str, str, Path]]) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    thumb_w = 270
    label_h = 36
    cols, rows = 4, 4
    # assume square-ish thumbs from 1080x1440
    sample = Image.open(webps[0][3])
    thumb_h = int(round(sample.height * (thumb_w / sample.width)))
    cell_w, cell_h = thumb_w + 16, thumb_h + label_h + 16
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(FONT_SANS_SRC), 14)
    except OSError:
        font = ImageFont.load_default()

    for i, (index, cid, nick, path) in enumerate(sorted(webps, key=lambda t: t[0])):
        r, c = divmod(i, cols)
        x0, y0 = c * cell_w + 8, r * cell_h + 8
        im = Image.open(path).convert("RGB")
        im = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (x0, y0))
        label = f"#{index} {cid} {nick}"
        draw.text((x0, y0 + thumb_h + 4), label, font=font, fill=(220, 210, 190))

    out = CONTACT_DIR / f"{sun}.jpg"
    quality = 85
    while quality >= 50:
        sheet.save(out, format="JPEG", quality=quality, optimize=True)
        if out.stat().st_size <= 2_000_000:
            break
        quality -= 5
    return out


def cmd_build(*, sign: Optional[str], only: Optional[list[str]]) -> int:
    print(build_fingerprint())
    data = load_cards_json()
    by_id = {c["id"]: c for c in data["cards"]}
    sans, serif = require_fonts(prefer_subset=True)

    targets: list[str]
    if only:
        targets = only
    elif sign:
        targets = [f"{m}_{sign}" for m in MBTI_ORDER]
    else:
        targets = [f"{m}_{s}" for s in SIGNS_ORDER for m in MBTI_ORDER]

    # group by sign for contact sheets
    by_sign: dict[str, list[str]] = {}
    for cid in targets:
        if cid not in by_id:
            print(f"ERROR unknown id {cid}")
            return 1
        sun = by_id[cid]["sun_en"]
        by_sign.setdefault(sun, []).append(cid)

    entries: dict[str, dict[str, Any]] = {}
    for sun, ids in by_sign.items():
        art = discover_art(sun)
        if not art:
            print(f"SKIP {sun}: no art directory / files")
            continue
        if len(art) < 16 and sign == sun:
            missing = sorted({f"{m}_{sun}" for m in MBTI_ORDER} - set(art))
            print(f"ERROR {sun}: incomplete art, missing {missing}")
            return 1
        built: list[tuple[int, str, str, Path]] = []
        for cid in ids:
            if cid not in art:
                print(f"SKIP {cid}: no unique art")
                continue
            row = by_id[cid]
            webp = compose_one(row, art[cid], sans_path=sans, serif_path=serif)
            idx = card_index(row["mbti"], sun)
            rel = f"assets/cards/webp/{cid}.webp"
            entries[cid] = {
                "id": cid,
                "webp": rel,
                "index": idx,
                "nickname": row["nickname"],
                "paradox": row["paradox"],
                "pct": row["pct"],
                "rarity_label": row["rarity_label"],
                "sun_en": sun,
                "mbti": row["mbti"],
            }
            built.append((idx, cid, row["nickname"], webp))
            print(f"OK {cid} -> {webp}")
        if built and (sign == sun or (sign is None and only is None) or all(c.endswith("_" + sun) for c in ids)):
            sheet = contact_sheet(sun, built)
            print(f"contact sheet {sheet} ({sheet.stat().st_size} bytes)")

    if not entries:
        print("ERROR: nothing built")
        return 1
    merge_manifest(entries)
    print(f"manifest updated: {MANIFEST_PATH} (+{len(entries)} entries)")
    return 0


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Offline 192 persona card compositor")
    p.add_argument("--normalize", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--sample-colors", action="store_true")
    p.add_argument("--subset-fonts", action="store_true", help="Rebuild font subsets from JSON text")
    p.add_argument("--sign", type=str, default=None)
    p.add_argument("--only", type=str, default=None, help="Comma-separated card ids")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    sign = args.sign.strip().title() if args.sign else None
    if sign == "Sagittarius" or (args.sign and args.sign.lower() == "sagittarius"):
        sign = "Sagittarius"
    if args.sign:
        # preserve exact map
        mapping = {s.lower(): s for s in SIGNS_ORDER}
        key = args.sign.strip().lower()
        if key not in mapping:
            print(f"ERROR unknown sign {args.sign}")
            return 1
        sign = mapping[key]

    if args.normalize:
        return cmd_normalize()
    if args.check:
        return cmd_check(sign=sign)
    if args.sample_colors:
        return cmd_sample_colors()
    if args.subset_fonts:
        return 0 if (subset_fonts(load_cards_json()) or True) else 1

    only = [x.strip() for x in args.only.split(",") if x.strip()] if args.only else None
    # ensure subsets exist before build
    if not (FONT_SANS_SUBSET.is_file() and FONT_SERIF_SUBSET.is_file()):
        subset_fonts(load_cards_json())
    return cmd_build(sign=sign, only=only)


if __name__ == "__main__":
    raise SystemExit(main())
