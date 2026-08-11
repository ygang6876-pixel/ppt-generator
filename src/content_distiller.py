from __future__ import annotations

import re


LABELS = {
    "risk": ["风险点", "控制措施", "责任要求", "检查验收"],
    "overview": ["工程位置", "关键参数", "施工范围", "控制要求"],
    "checklist": ["执行要求", "过程控制", "责任落实", "验收闭环"],
}


def distill_slide_items(title: str, body: list[str], bullets: list[str], layout: str) -> tuple[list[str], list[str]]:
    items = [_clean(item) for item in [*body, *bullets] if _clean(item)]
    if not items:
        return body, bullets

    if layout == "process":
        return [], _distill_process(items)
    if layout == "risk":
        return [], _distill_labeled(items, LABELS["risk"], 42)
    if layout == "overview":
        return [], _distill_labeled(items, LABELS["overview"], 44)
    if layout == "checklist":
        return [], _distill_labeled(items, LABELS["checklist"], 44)
    if layout in {"highlight", "summary"}:
        return [], [_shorten(_key_sentence(item), 48) for item in items[:5]]
    return [_shorten(_key_sentence(item), 56) for item in items[:3]], []


def summarize_table_for_report(headers: list[str], rows: list[list[str]]) -> tuple[list[str], list[str]]:
    row_count = len(rows)
    col_count = len(headers)
    compact_headers = "、".join(_shorten(header, 8) for header in headers[:5] if header)
    body = [f"源表格共 {row_count} 行、{col_count} 列；汇报版提取字段和代表项，避免压缩失真。"]
    bullets = [f"字段：{compact_headers}" if compact_headers else "字段：见源表格"]
    for row in rows[:3]:
        values = [_shorten(value, 14) for value in row[:3] if value]
        if values:
            bullets.append(" / ".join(values))
    return body, bullets[:4]


def _distill_process(items: list[str]) -> list[str]:
    steps: list[str] = []
    for item in items:
        parts = re.split(r"→|->|=>|；|;|，|,", item)
        for part in parts:
            cleaned = _shorten(_strip_prefix(part), 24)
            if cleaned and cleaned not in steps:
                steps.append(cleaned)
            if len(steps) >= 4:
                return steps
    return steps[:4]


def _distill_labeled(items: list[str], labels: list[str], limit: int) -> list[str]:
    values = [_shorten(_key_sentence(item), limit) for item in items[: len(labels)]]
    return [f"{label}：{value}" for label, value in zip(labels, values)]


def _key_sentence(text: str) -> str:
    text = _strip_prefix(_clean(text))
    sentences = [part.strip() for part in re.split(r"。|；|;", text) if part.strip()]
    if not sentences:
        return text
    scored = sorted(sentences, key=_sentence_score, reverse=True)
    return scored[0]


def _sentence_score(sentence: str) -> tuple[int, int]:
    keywords = [
        "必须",
        "严禁",
        "应",
        "不得",
        "控制",
        "检查",
        "验收",
        "风险",
        "安全",
        "质量",
        "施工",
        "开挖",
        "支护",
        "监测",
    ]
    score = sum(1 for keyword in keywords if keyword in sentence)
    if re.search(r"\d", sentence):
        score += 1
    return score, -len(sentence)


def _strip_prefix(text: str) -> str:
    text = _clean(text)
    text = re.sub(r"^([（(]?\d+[）).、]|[①②③④⑤⑥⑦⑧⑨⑩]|[-•])\s*", "", text)
    text = re.sub(r"^(应|必须|需要|要求|确保|严格)\s*", "", text)
    return text


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _shorten(text: str, limit: int) -> str:
    text = _clean(text)
    if len(text) <= limit:
        return text
    trimmed = re.split(r"，|、|；|。|,|;", text[: limit + 1].rstrip())[0]
    if 8 <= len(trimmed) <= limit:
        return trimmed
    return text[:limit].rstrip()
