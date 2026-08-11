from pathlib import Path

from docx import Document

from .markdown_parser import Deck, Slide, Table


def parse_docx(path: Path) -> Deck:
    document = Document(path)
    title = _document_title(document, path)
    subtitle = "Generated from WPS/Word document"
    slides: list[Slide] = []
    current: Slide | None = None

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        style_name = paragraph.style.name if paragraph.style is not None else ""
        if _is_heading(style_name):
            current = Slide(title=text)
            slides.append(current)
            continue

        if current is None:
            subtitle = text
            current = Slide(title="内容")
            slides.append(current)
            continue

        if _is_list(paragraph):
            current.bullets.append(text)
        else:
            current.body.append(text)

    if document.tables:
        table_slide = current if current is not None else Slide(title="表格")
        if current is None:
            slides.append(table_slide)
        for docx_table in document.tables:
            table = _convert_table(docx_table)
            if table is not None:
                table_slide.tables.append(table)

    if not slides:
        slides.append(Slide(title="内容", body=["该文档未读取到正文内容。"]))

    return Deck(title=title, subtitle=subtitle, slides=slides)


def _document_title(document, path: Path) -> str:
    if document.core_properties.title:
        return document.core_properties.title
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            return text
    return path.stem


def _is_heading(style_name: str) -> bool:
    normalized = style_name.lower()
    return normalized.startswith("heading") or style_name.startswith("标题")


def _is_list(paragraph) -> bool:
    style_name = paragraph.style.name if paragraph.style is not None else ""
    return "list" in style_name.lower() or "列表" in style_name


def _convert_table(docx_table) -> Table | None:
    rows = [[cell.text.strip() for cell in row.cells] for row in docx_table.rows]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return None
    if len(rows) == 1:
        headers = [f"列{index + 1}" for index in range(len(rows[0]))]
        data_rows = rows
    else:
        headers = rows[0]
        data_rows = rows[1:]
    col_count = len(headers)
    return Table(headers=headers, rows=[_normalize_row(row, col_count) for row in data_rows])


def _normalize_row(row: list[str], size: int) -> list[str]:
    if len(row) < size:
        return row + [""] * (size - len(row))
    return row[:size]
