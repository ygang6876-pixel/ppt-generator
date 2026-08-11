from __future__ import annotations

import re
from dataclasses import dataclass, field

from .markdown_parser import Table


@dataclass
class TablePlan:
    layout: str
    body: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)


NUMERIC_HEADERS = re.compile(r"数量|工程量|方量|长度|面积|体积|重量|金额|合计|单价|孔数|孔深|装药|kg|m3|m²|m³|mm")
SCHEDULE_HEADERS = re.compile(r"时间|日期|开始|完成|工期|进度|节点")
TIME_HEADERS = re.compile(r"时间|日期|开始|完成|工期")
LOCATION_HEADERS = re.compile(r"部位|位置|桩号|里程|工程部位|项目|名称")
UNIT_HEADERS = re.compile(r"单位|规格|型号")


def plan_table_for_report(title: str, table: Table) -> TablePlan:
    headers = [_clean(cell) for cell in table.headers]
    rows = [[_clean(cell) for cell in row] for row in table.rows if any(_clean(cell) for cell in row)]
    row_count = len(rows)
    col_count = len(headers)
    text_size = _table_text_length(headers, rows)

    if not headers or not rows:
        return TablePlan(layout="summary", body=["源表格为空，建议回到原文核对。"])

    if _looks_like_schedule(title, headers):
        return _schedule_plan(headers, rows, row_count, col_count)

    if _looks_like_quantity_table(title, headers):
        return _quantity_plan(headers, rows, row_count, col_count)

    if row_count <= 6 and col_count <= 5 and text_size <= 320:
        return TablePlan(layout="full-table", tables=[Table(headers=headers, rows=rows)])

    if col_count > 5:
        key_table = _compact_key_table(headers, rows)
        return TablePlan(
            layout="full-table" if len(key_table.rows) <= 6 else "checklist",
            body=[],
            bullets=[] if len(key_table.rows) <= 6 else _representative_rows(headers, rows, limit=3),
            tables=[key_table] if len(key_table.rows) <= 6 else [],
        )

    return TablePlan(
        layout="checklist",
        body=[f"源表格共 {row_count} 行、{col_count} 列；已转成汇报摘要，避免表格压缩失真。"],
        bullets=_representative_rows(headers, rows, limit=4),
    )


def _quantity_plan(headers: list[str], rows: list[list[str]], row_count: int, col_count: int) -> TablePlan:
    label_idx = _first_index(headers, LOCATION_HEADERS) or 0
    value_idx = _first_index(headers, NUMERIC_HEADERS)
    unit_idx = _first_index(headers, UNIT_HEADERS)
    bullets: list[str] = []
    for row in rows:
        label = _cell(row, label_idx)
        value = _cell(row, value_idx) if value_idx is not None else _first_number(row)
        unit = _cell(row, unit_idx) if unit_idx is not None else ""
        if label and value:
            bullets.append(_shorten(f"{value}{unit}：{label}", 42))
        if len(bullets) >= 4:
            break
    if not bullets:
        bullets = _representative_rows(headers, rows, limit=4)
    return TablePlan(
        layout="metrics",
        body=[],
        bullets=bullets,
    )


def _schedule_plan(headers: list[str], rows: list[list[str]], row_count: int, col_count: int) -> TablePlan:
    label_idx = _first_index(headers, LOCATION_HEADERS) or 0
    time_idx = _first_index(headers, TIME_HEADERS)
    bullets: list[str] = []
    for row in rows:
        label = _cell(row, label_idx)
        time_value = _cell(row, time_idx) if time_idx is not None else _first_date_or_number(row)
        if label and time_value:
            bullets.append(_shorten(f"{time_value}：{label}", 42))
        if len(bullets) >= 4:
            break
    if not bullets:
        bullets = _representative_rows(headers, rows, limit=4)
    return TablePlan(
        layout="timeline",
        body=[],
        bullets=bullets,
    )


def _compact_key_table(headers: list[str], rows: list[list[str]]) -> Table:
    key_indexes = _key_column_indexes(headers)
    compact_headers = [headers[index] for index in key_indexes]
    compact_rows = [[_cell(row, index) for index in key_indexes] for row in rows[:6]]
    return Table(headers=compact_headers, rows=compact_rows)


def _key_column_indexes(headers: list[str]) -> list[int]:
    indexes: list[int] = []
    for pattern in [LOCATION_HEADERS, NUMERIC_HEADERS, UNIT_HEADERS, SCHEDULE_HEADERS]:
        index = _first_index(headers, pattern)
        if index is not None and index not in indexes:
            indexes.append(index)
    if 0 not in indexes:
        indexes.insert(0, 0)
    for index in range(len(headers)):
        if len(indexes) >= 5:
            break
        if index not in indexes:
            indexes.append(index)
    return indexes[:5]


def _representative_rows(headers: list[str], rows: list[list[str]], limit: int) -> list[str]:
    indexes = _key_column_indexes(headers)
    bullets: list[str] = []
    for row in rows[:limit]:
        values = [_cell(row, index) for index in indexes[:3]]
        values = [value for value in values if value]
        if values:
            bullets.append(_shorten(" / ".join(values), 46))
    return bullets


def _looks_like_quantity_table(title: str, headers: list[str]) -> bool:
    joined = f"{title} {' '.join(headers)}"
    return bool(NUMERIC_HEADERS.search(joined) and LOCATION_HEADERS.search(joined))


def _looks_like_schedule(title: str, headers: list[str]) -> bool:
    joined = f"{title} {' '.join(headers)}"
    return bool(SCHEDULE_HEADERS.search(joined))


def _first_index(headers: list[str], pattern: re.Pattern[str]) -> int | None:
    for index, header in enumerate(headers):
        if pattern.search(header):
            return index
    return None


def _first_number(row: list[str]) -> str:
    for cell in row:
        match = re.search(r"\d+(?:\.\d+)?", cell)
        if match:
            return match.group(0)
    return ""


def _first_date_or_number(row: list[str]) -> str:
    for cell in row:
        if re.search(r"\d{1,4}[-./年月]\d{1,2}|\d+(?:\.\d+)?", cell):
            return cell
    return ""


def _cell(row: list[str], index: int | None) -> str:
    if index is None or index >= len(row):
        return ""
    return row[index]


def _table_text_length(headers: list[str], rows: list[list[str]]) -> int:
    return sum(len(cell) for cell in headers) + sum(len(cell) for row in rows for cell in row)


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
