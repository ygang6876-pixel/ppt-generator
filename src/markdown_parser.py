from dataclasses import dataclass, field
import re


IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")
LAYOUT_PATTERN = re.compile(r"<!--\s*layout:\s*(?P<layout>[a-zA-Z0-9_-]+)\s*-->")


@dataclass
class ImageAsset:
    alt: str
    path: str


@dataclass
class Table:
    headers: list[str]
    rows: list[list[str]]


@dataclass
class MermaidDiagram:
    code: str


@dataclass
class CodeBlock:
    language: str
    code: str


@dataclass
class Slide:
    title: str
    bullets: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)
    images: list[ImageAsset] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    mermaid: list[MermaidDiagram] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    layout: str = "auto"


@dataclass
class Deck:
    title: str
    subtitle: str
    slides: list[Slide]
    metadata: dict[str, str] = field(default_factory=dict)


def parse_markdown(markdown: str) -> Deck:
    metadata, content = _extract_front_matter(markdown)
    title = metadata.get("title", "Untitled Presentation")
    subtitle = metadata.get("subtitle", "Generated from Markdown")
    slides: list[Slide] = []
    current: Slide | None = None
    pending_layout = "auto"
    lines = [line.strip() for line in content.splitlines()]
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line:
            index += 1
            continue

        layout_match = LAYOUT_PATTERN.fullmatch(line)
        if layout_match:
            pending_layout = layout_match.group("layout").strip().lower() or "auto"
            index += 1
            continue

        if line.startswith("# "):
            title = line[2:].strip() or title
            index += 1
            continue

        if line.startswith("### "):
            text = line[4:].strip()
            if current is None:
                current = Slide(title=text, layout=pending_layout)
                pending_layout = "auto"
                slides.append(current)
            else:
                current.body.append(text)
            index += 1
            continue

        if line.startswith("## "):
            current = Slide(title=line[3:].strip(), layout=pending_layout)
            pending_layout = "auto"
            slides.append(current)
            index += 1
            continue

        mermaid = _parse_mermaid_at(lines, index)
        if mermaid is not None:
            if current is None:
                current = Slide(title="\u5185\u5bb9", layout=pending_layout)
                pending_layout = "auto"
                slides.append(current)
            current.mermaid.append(mermaid)
            index += len(mermaid.code.splitlines()) + 2
            continue

        code_block = _parse_code_at(lines, index)
        if code_block is not None:
            if current is None:
                current = Slide(title="\u5185\u5bb9", layout=pending_layout)
                pending_layout = "auto"
                slides.append(current)
            current.code_blocks.append(code_block)
            index += len(code_block.code.splitlines()) + 2
            continue

        table = _parse_table_at(lines, index)
        if table is not None:
            if current is None:
                current = Slide(title="\u5185\u5bb9", layout=pending_layout)
                pending_layout = "auto"
                slides.append(current)
            current.tables.append(table)
            index += len(table.rows) + 2
            continue

        image_match = IMAGE_PATTERN.fullmatch(line)
        if image_match:
            if current is None:
                current = Slide(title="\u5185\u5bb9", layout=pending_layout)
                pending_layout = "auto"
                slides.append(current)
            current.images.append(
                ImageAsset(
                    alt=image_match.group("alt").strip(),
                    path=image_match.group("path").strip(),
                )
            )
            index += 1
            continue

        if line.startswith(("- ", "* ")):
            if current is None:
                current = Slide(title="\u5185\u5bb9", layout=pending_layout)
                pending_layout = "auto"
                slides.append(current)
            current.bullets.append(line[2:].strip())
            index += 1
            continue

        if current is None:
            subtitle = line
        else:
            current.body.append(line)
        index += 1

    if not slides:
        slides.append(Slide(title="\u5185\u5bb9", body=[subtitle], layout=pending_layout))

    return Deck(title=title, subtitle=subtitle, slides=slides, metadata=metadata)


def _parse_mermaid_at(lines: list[str], index: int) -> MermaidDiagram | None:
    if lines[index].lower() != "```mermaid":
        return None
    code_lines: list[str] = []
    row_index = index + 1
    while row_index < len(lines):
        if lines[row_index] == "```":
            code = "\n".join(code_lines).strip()
            return MermaidDiagram(code=code) if code else None
        code_lines.append(lines[row_index])
        row_index += 1
    return None


def _parse_code_at(lines: list[str], index: int) -> CodeBlock | None:
    line = lines[index]
    if not line.startswith("```") or line.lower() == "```mermaid":
        return None
    language = line[3:].strip() or "text"
    code_lines: list[str] = []
    row_index = index + 1
    while row_index < len(lines):
        if lines[row_index] == "```":
            code = "\n".join(code_lines)
            return CodeBlock(language=language, code=code)
        code_lines.append(lines[row_index])
        row_index += 1
    return None


def _extract_front_matter(markdown: str) -> tuple[dict[str, str], str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown

    metadata: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return metadata, "\n".join(lines[index + 1 :])
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip().strip('"').strip("'")
    return metadata, markdown


def _parse_table_at(lines: list[str], index: int) -> Table | None:
    if index + 1 >= len(lines):
        return None
    header_line = lines[index]
    separator_line = lines[index + 1]
    if not (_is_table_row(header_line) and _is_table_separator(separator_line)):
        return None

    headers = _split_table_row(header_line)
    rows: list[list[str]] = []
    row_index = index + 2
    while row_index < len(lines) and _is_table_row(lines[row_index]):
        row = _split_table_row(lines[row_index])
        rows.append(_normalize_row(row, len(headers)))
        row_index += 1

    if not headers or not rows:
        return None
    return Table(headers=headers, rows=rows)


def _is_table_row(line: str) -> bool:
    return line.startswith("|") and line.endswith("|") and line.count("|") >= 2


def _is_table_separator(line: str) -> bool:
    cells = _split_table_row(line)
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip("|").split("|")]


def _normalize_row(row: list[str], size: int) -> list[str]:
    if len(row) < size:
        return row + [""] * (size - len(row))
    return row[:size]
