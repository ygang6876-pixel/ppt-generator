from dataclasses import dataclass

from pptx.dml.color import RGBColor


@dataclass(frozen=True)
class Theme:
    title_font: str
    body_font: str
    cover_background: RGBColor
    slide_background: RGBColor
    title_color: RGBColor
    cover_title_color: RGBColor
    cover_subtitle_color: RGBColor
    body_color: RGBColor
    accent_color: RGBColor
    footer_color: RGBColor


DEFAULT_THEME = Theme(
    title_font="Microsoft YaHei",
    body_font="Microsoft YaHei",
    cover_background=RGBColor(18, 40, 70),
    slide_background=RGBColor(248, 250, 252),
    title_color=RGBColor(20, 55, 85),
    cover_title_color=RGBColor(255, 255, 255),
    cover_subtitle_color=RGBColor(220, 230, 240),
    body_color=RGBColor(30, 41, 59),
    accent_color=RGBColor(31, 111, 235),
    footer_color=RGBColor(100, 116, 139),
)
