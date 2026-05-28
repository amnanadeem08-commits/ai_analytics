"""Brand theme helpers — logo upload, palette extraction, export styling."""

from __future__ import annotations

import io
from dataclasses import dataclass, field, asdict
from typing import Any

from config import CHART_COLORS

DEFAULT_PRIMARY = "#5046E4"
DEFAULT_SECONDARY = "#7C3AED"
DEFAULT_ACCENT = "#0E9F6E"


@dataclass
class BrandTheme:
    primary: str = DEFAULT_PRIMARY
    secondary: str = DEFAULT_SECONDARY
    accent: str = DEFAULT_ACCENT
    palette: list[str] = field(default_factory=lambda: list(CHART_COLORS))
    logo_bytes: bytes | None = None
    company_name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "BrandTheme":
        if not data:
            return cls()
        palette = data.get("palette") or list(CHART_COLORS)
        return cls(
            primary=data.get("primary", DEFAULT_PRIMARY),
            secondary=data.get("secondary", DEFAULT_SECONDARY),
            accent=data.get("accent", DEFAULT_ACCENT),
            palette=list(palette),
            logo_bytes=data.get("logo_bytes"),
            company_name=data.get("company_name", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def _is_neutral(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    if max(r, g, b) < 28 or min(r, g, b) > 232:
        return True
    spread = max(r, g, b) - min(r, g, b)
    return spread < 18 and 40 < max(r, g, b) < 215


def extract_palette_from_logo(logo_bytes: bytes, max_colors: int = 6) -> list[str]:
    """Extract dominant non-neutral colors from a logo image."""
    try:
        from PIL import Image
    except ImportError:
        return list(CHART_COLORS[:max_colors])

    img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
    img = img.resize((120, 120))
    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
    rgb_img.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
    quantized = rgb_img.quantize(colors=max_colors + 4, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    counts = quantized.histogram()
    ranked: list[tuple[int, tuple[int, int, int]]] = []

    for idx, count in enumerate(counts):
        if count <= 0:
            continue
        base = idx * 3
        rgb = (palette[base], palette[base + 1], palette[base + 2])
        if _is_neutral(rgb):
            continue
        ranked.append((count, rgb))

    ranked.sort(key=lambda item: item[0], reverse=True)
    colors = [rgb_to_hex(*rgb) for _, rgb in ranked[:max_colors]]
    return colors or list(CHART_COLORS[:max_colors])


def build_brand_theme(
    logo_bytes: bytes | None = None,
    primary: str | None = None,
    secondary: str | None = None,
    accent: str | None = None,
    company_name: str = "",
) -> BrandTheme:
    palette = extract_palette_from_logo(logo_bytes) if logo_bytes else list(CHART_COLORS)
    return BrandTheme(
        primary=primary or palette[0] if palette else DEFAULT_PRIMARY,
        secondary=secondary or (palette[1] if len(palette) > 1 else DEFAULT_SECONDARY),
        accent=accent or (palette[2] if len(palette) > 2 else DEFAULT_ACCENT),
        palette=palette or list(CHART_COLORS),
        logo_bytes=logo_bytes,
        company_name=company_name.strip(),
    )


def summary_bullets(summary_text: str, limit: int = 5) -> list[str]:
    """Turn executive summary prose into short slide bullets."""
    clean = summary_text.replace("**", "").replace("##", "").strip()
    if not clean:
        return ["Analytics insights will appear here once AI summary is generated."]

    chunks: list[str] = []
    for block in clean.split("\n"):
        block = block.strip()
        if not block:
            continue
        for sentence in block.replace("•", ".").split("."):
            sentence = sentence.strip()
            if len(sentence) >= 24:
                chunks.append(sentence if sentence.endswith(".") else f"{sentence}.")
            if len(chunks) >= limit:
                return chunks[:limit]

    if not chunks:
        chunks = [clean[:220] + ("…" if len(clean) > 220 else "")]
    return chunks[:limit]
