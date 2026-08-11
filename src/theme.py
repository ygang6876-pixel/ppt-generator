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
    table_header: RGBColor


THEMES = {
    "business": Theme(
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
        table_header=RGBColor(20, 55, 85),
    ),
    "clean": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(246, 247, 249),
        slide_background=RGBColor(255, 255, 255),
        title_color=RGBColor(17, 24, 39),
        cover_title_color=RGBColor(17, 24, 39),
        cover_subtitle_color=RGBColor(75, 85, 99),
        body_color=RGBColor(55, 65, 81),
        accent_color=RGBColor(22, 163, 74),
        footer_color=RGBColor(107, 114, 128),
        table_header=RGBColor(17, 24, 39),
    ),
    "dark": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(15, 23, 42),
        slide_background=RGBColor(17, 24, 39),
        title_color=RGBColor(241, 245, 249),
        cover_title_color=RGBColor(255, 255, 255),
        cover_subtitle_color=RGBColor(203, 213, 225),
        body_color=RGBColor(226, 232, 240),
        accent_color=RGBColor(56, 189, 248),
        footer_color=RGBColor(148, 163, 184),
        table_header=RGBColor(30, 41, 59),
    ),
}

DEFAULT_THEME = THEMES["business"]


def get_theme(name: str | None) -> Theme:
    return THEMES.get((name or "business").lower(), DEFAULT_THEME)
