from src.markdown_parser import parse_markdown


def test_parse_front_matter_and_basic_slide():
    deck = parse_markdown(
        """---
title: Demo Deck
subtitle: Generated example
theme: tech
footer: Demo footer
---

# Demo Deck

Intro text.

## Goals

- Parse Markdown
- Generate PPT
"""
    )

    assert deck.title == "Demo Deck"
    assert deck.subtitle == "Intro text."
    assert deck.metadata["subtitle"] == "Generated example"
    assert deck.metadata["theme"] == "tech"
    assert deck.metadata["footer"] == "Demo footer"
    assert len(deck.slides) == 1
    assert deck.slides[0].title == "Goals"
    assert deck.slides[0].bullets == ["Parse Markdown", "Generate PPT"]


def test_parse_table_mermaid_and_code_blocks():
    deck = parse_markdown(
        """# Demo

<!-- layout: full-table -->
## Table

| Module | Status |
| --- | --- |
| Parser | Done |

<!-- layout: diagram -->
## Flow

```mermaid
flowchart LR
  A --> B
```

<!-- layout: code -->
## Code

```python
print("ok")
```
"""
    )

    assert deck.slides[0].tables[0].headers == ["Module", "Status"]
    assert deck.slides[0].tables[0].rows == [["Parser", "Done"]]
    assert deck.slides[1].mermaid[0].code.startswith("flowchart LR")
    assert deck.slides[2].code_blocks[0].language == "python"
