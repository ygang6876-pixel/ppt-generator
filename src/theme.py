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
    subtle_fill: RGBColor


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
        subtle_fill=RGBColor(226, 232, 240),
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
        subtle_fill=RGBColor(243, 244, 246),
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
        subtle_fill=RGBColor(30, 41, 59),
    ),
    "midnight": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(11, 18, 32),
        slide_background=RGBColor(13, 24, 38),
        title_color=RGBColor(236, 244, 255),
        cover_title_color=RGBColor(255, 255, 255),
        cover_subtitle_color=RGBColor(184, 199, 217),
        body_color=RGBColor(220, 230, 242),
        accent_color=RGBColor(94, 234, 212),
        footer_color=RGBColor(145, 165, 190),
        table_header=RGBColor(22, 78, 99),
        subtle_fill=RGBColor(22, 36, 55),
    ),
    "emerald": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(8, 61, 57),
        slide_background=RGBColor(247, 252, 249),
        title_color=RGBColor(10, 83, 78),
        cover_title_color=RGBColor(255, 255, 255),
        cover_subtitle_color=RGBColor(210, 239, 231),
        body_color=RGBColor(31, 47, 43),
        accent_color=RGBColor(16, 185, 129),
        footer_color=RGBColor(91, 112, 108),
        table_header=RGBColor(10, 83, 78),
        subtle_fill=RGBColor(220, 245, 236),
    ),
    "sunrise": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(111, 38, 49),
        slide_background=RGBColor(255, 251, 247),
        title_color=RGBColor(111, 38, 49),
        cover_title_color=RGBColor(255, 255, 255),
        cover_subtitle_color=RGBColor(255, 226, 214),
        body_color=RGBColor(61, 48, 43),
        accent_color=RGBColor(244, 114, 72),
        footer_color=RGBColor(139, 100, 91),
        table_header=RGBColor(111, 38, 49),
        subtle_fill=RGBColor(255, 235, 220),
    ),
    "ivory": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(46, 50, 56),
        slide_background=RGBColor(250, 250, 246),
        title_color=RGBColor(43, 46, 52),
        cover_title_color=RGBColor(255, 255, 255),
        cover_subtitle_color=RGBColor(231, 232, 225),
        body_color=RGBColor(67, 70, 76),
        accent_color=RGBColor(180, 83, 9),
        footer_color=RGBColor(116, 120, 128),
        table_header=RGBColor(46, 50, 56),
        subtle_fill=RGBColor(236, 236, 229),
    ),
    "tech": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(21, 32, 64),
        slide_background=RGBColor(246, 249, 255),
        title_color=RGBColor(21, 32, 64),
        cover_title_color=RGBColor(255, 255, 255),
        cover_subtitle_color=RGBColor(213, 225, 255),
        body_color=RGBColor(39, 50, 77),
        accent_color=RGBColor(79, 70, 229),
        footer_color=RGBColor(98, 111, 146),
        table_header=RGBColor(21, 32, 64),
        subtle_fill=RGBColor(230, 236, 255),
    ),
    "construction": Theme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        cover_background=RGBColor(36, 39, 43),
        slide_background=RGBColor(248, 249, 247),
        title_color=RGBColor(40, 44, 50),
        cover_title_color=RGBColor(255, 255, 255),
        cover_subtitle_color=RGBColor(239, 230, 214),
        body_color=RGBColor(47, 52, 58),
        accent_color=RGBColor(214, 116, 31),
        footer_color=RGBColor(111, 116, 124),
        table_header=RGBColor(49, 55, 63),
        subtle_fill=RGBColor(239, 232, 219),
    ),
}

DEFAULT_THEME = THEMES["business"]


def get_theme(name: str | None) -> Theme:
    return THEMES.get((name or "business").lower(), DEFAULT_THEME)
