from dataclasses import dataclass, field
import re


IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")


@dataclass
class ImageAsset:
    alt: str
    path: str


@dataclass
class Table:
    headers: list[str]
    rows: list[list[str]]


@dataclass
class Slide:
    title: str
    bullets: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)
    images: list[ImageAsset] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)


@dataclass
class Deck:
    title: str
    subtitle: str
    slides: list[Slide]


def parse_markdown(markdown: str) -> Deck:
    title = "Untitled Presentation"
    subtitle = "Generated from Markdown"
    slides: list[Slide] = []
    current: Slide | None = None
    lines = [line.strip() for line in markdown.splitlines()]
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line:
            index += 1
            continue

        if line.startswith("# "):
            title = line[2:].strip() or title
            index += 1
            continue

        if line.startswith("### "):
            text = line[4:].strip()
            if current is None:
                current = Slide(title=text)
                slides.append(current)
            else:
                current.body.append(text)
            index += 1
            continue

        if line.startswith("## "):
            current = Slide(title=line[3:].strip())
            slides.append(current)
            index += 1
            continue

        table = _parse_table_at(lines, index)
        if table is not None:
            if current is None:
                current = Slide(title="内容")
                slides.append(current)
            current.tables.append(table)
            index += len(table.rows) + 2
            continue

        image_match = IMAGE_PATTERN.fullmatch(line)
        if image_match:
            if current is None:
                current = Slide(title="内容")
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
                current = Slide(title="内容")
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
        slides.append(Slide(title="内容", body=[subtitle]))

    return Deck(title=title, subtitle=subtitle, slides=slides)


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
