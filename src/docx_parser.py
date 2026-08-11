from __future__ import annotations

from pathlib import Path
import re

from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml.ns import qn
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph

from .markdown_parser import Deck, ImageAsset, Slide, Table


MAX_TEXT_ITEMS_PER_SLIDE = 6
CAPTION_STYLE_NAMES = {"caption", "题注"}


def parse_docx(path: Path) -> Deck:
    document = Document(path)
    title = _document_title(document, path)
    subtitle = _document_subtitle(document)
    slides: list[Slide] = []
    current: Slide | None = None
    pending_caption: str | None = None
    media_dir = path.parent / f"{path.stem}_assets"
    image_index = 1

    for block in _iter_blocks(document):
        if isinstance(block, Paragraph):
            text = _clean_text(block.text)
            style_name = block.style.name if block.style is not None else ""

            if _is_toc(style_name):
                continue

            images = _extract_paragraph_images(block, media_dir, image_index)
            image_index += len(images)

            if images and current is None and pending_caption is None:
                continue

            if text and _is_caption(style_name, text):
                pending_caption = text
                if images:
                    slides.append(
                        Slide(
                            title=text,
                            body=[],
                            images=images,
                            layout="image-full",
                        )
                    )
                    pending_caption = None
                continue

            if images:
                image_title = pending_caption or text or (current.title if current else "图片")
                image_body = [] if pending_caption else ([text] if text else [])
                slides.append(
                    Slide(
                        title=image_title,
                        body=image_body[:2],
                        images=images,
                        layout="image-full" if len(images) == 1 else "image-right",
                    )
                )
                pending_caption = None
                continue

            if not text:
                continue

            if _is_section_heading(style_name):
                current = Slide(title=text)
                slides.append(current)
                pending_caption = None
                continue

            if _is_minor_heading(style_name):
                if current is None:
                    current = Slide(title=text)
                    slides.append(current)
                else:
                    _append_text(current, text)
                pending_caption = None
                continue

            if current is None:
                current = Slide(title="内容")
                slides.append(current)

            if _is_list(block):
                _append_bullet(current, text)
            else:
                _append_text(current, text)

        elif isinstance(block, DocxTable):
            table = _convert_table(block)
            if table is None:
                continue

            table_title = pending_caption or "表格"
            slides.append(
                Slide(
                    title=table_title,
                    tables=[table],
                    layout="full-table",
                )
            )
            pending_caption = None

    slides = _remove_empty_slides(slides)
    if not slides:
        raise ValueError("该文档未读取到可生成 PPT 的正文内容。")

    return Deck(
        title=title,
        subtitle=subtitle,
        slides=slides,
        metadata={"theme": "construction", "footer": "PPT Generator"},
    )


def _iter_blocks(document: DocxDocument):
    body = document.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield DocxTable(child, document)


def _document_title(document, path: Path) -> str:
    if document.core_properties.title:
        return document.core_properties.title
    for paragraph in document.paragraphs:
        text = _clean_text(paragraph.text)
        if text and not _is_toc(paragraph.style.name if paragraph.style else ""):
            return text
    return path.stem


def _document_subtitle(document) -> str:
    lines: list[str] = []
    for paragraph in document.paragraphs:
        text = _clean_text(paragraph.text)
        style_name = paragraph.style.name if paragraph.style is not None else ""
        if not text or _is_toc(style_name):
            continue
        if _is_section_heading(style_name):
            break
        lines.append(text)
        if len(lines) >= 3:
            break
    return " / ".join(lines[1:3]) if len(lines) > 1 else "Generated from WPS/Word document"


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _is_toc(style_name: str) -> bool:
    return style_name.lower().startswith("toc")


def _heading_level(style_name: str) -> int | None:
    normalized = style_name.lower()
    match = re.match(r"heading\s+(\d+)", normalized)
    if match:
        return int(match.group(1))
    match = re.match(r"标题\s*(\d+)", style_name)
    if match:
        return int(match.group(1))
    return None


def _is_section_heading(style_name: str) -> bool:
    level = _heading_level(style_name)
    return level is not None and level <= 3


def _is_minor_heading(style_name: str) -> bool:
    level = _heading_level(style_name)
    return level is not None and 3 < level < 6


def _is_caption(style_name: str, text: str) -> bool:
    normalized = style_name.lower()
    if normalized in CAPTION_STYLE_NAMES or style_name in CAPTION_STYLE_NAMES:
        return True
    return bool(re.match(r"^(图|表)\s*\d", text)) or _heading_level(style_name) == 6


def _is_list(paragraph) -> bool:
    style_name = paragraph.style.name if paragraph.style is not None else ""
    if "list" in style_name.lower() or "列表" in style_name:
        return True
    text = _clean_text(paragraph.text)
    return bool(re.match(r"^([（(]?\d+[）).、]|[①②③④⑤⑥⑦⑧⑨⑩]|[-•])", text))


def _append_text(slide: Slide, text: str) -> None:
    if not text:
        return
    if len(slide.body) + len(slide.bullets) < MAX_TEXT_ITEMS_PER_SLIDE:
        slide.body.append(_shorten(text))


def _append_bullet(slide: Slide, text: str) -> None:
    if not text:
        return
    if len(slide.body) + len(slide.bullets) < MAX_TEXT_ITEMS_PER_SLIDE:
        slide.bullets.append(_shorten(text))


def _shorten(text: str, limit: int = 120) -> str:
    text = _clean_text(text)
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def _extract_paragraph_images(paragraph: Paragraph, media_dir: Path, start_index: int) -> list[ImageAsset]:
    images: list[ImageAsset] = []
    for offset, blip in enumerate(paragraph._element.iter(qn("a:blip"))):
        rel_id = blip.get(qn("r:embed"))
        if not rel_id or rel_id not in paragraph.part.related_parts:
            continue
        image_part = paragraph.part.related_parts[rel_id]
        ext = Path(str(image_part.partname)).suffix or _extension_from_content_type(image_part.content_type)
        media_dir.mkdir(parents=True, exist_ok=True)
        filename = f"docx_image_{start_index + offset:03d}{ext.lower()}"
        image_path = media_dir / filename
        if not image_path.exists():
            image_path.write_bytes(image_part.blob)
        images.append(ImageAsset(alt=paragraph.text.strip() or image_path.stem, path=str(image_path.relative_to(media_dir.parent))))
    return images


def _extension_from_content_type(content_type: str) -> str:
    mapping = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
    }
    return mapping.get(content_type, ".png")


def _convert_table(docx_table: DocxTable) -> Table | None:
    rows = [[_clean_text(cell.text) for cell in row.cells] for row in docx_table.rows]
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


def _remove_empty_slides(slides: list[Slide]) -> list[Slide]:
    return [
        slide
        for slide in slides
        if slide.body or slide.bullets or slide.images or slide.tables or slide.mermaid or slide.code_blocks
    ]
