from dataclasses import dataclass, field
import re


IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")


@dataclass
class ImageAsset:
    alt: str
    path: str


@dataclass
class Slide:
    title: str
    bullets: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)
    images: list[ImageAsset] = field(default_factory=list)


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

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("# "):
            title = line[2:].strip() or title
            continue

        if line.startswith("### "):
            text = line[4:].strip()
            if current is None:
                current = Slide(title=text)
                slides.append(current)
            else:
                current.body.append(text)
            continue

        if line.startswith("## "):
            current = Slide(title=line[3:].strip())
            slides.append(current)
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
            continue

        if line.startswith(("- ", "* ")):
            if current is None:
                current = Slide(title="内容")
                slides.append(current)
            current.bullets.append(line[2:].strip())
            continue

        if current is None:
            subtitle = line
        else:
            current.body.append(line)

    if not slides:
        slides.append(Slide(title="内容", body=[subtitle]))

    return Deck(title=title, subtitle=subtitle, slides=slides)
