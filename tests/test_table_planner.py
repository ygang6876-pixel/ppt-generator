from src.markdown_parser import Table
from src.table_planner import plan_table_for_report


def test_quantity_table_becomes_metrics_plan():
    table = Table(
        headers=["序号", "工程部位", "单位", "工程量"],
        rows=[
            ["1", "截水沟", "m", "120"],
            ["2", "锚杆", "根", "80"],
        ],
    )

    plan = plan_table_for_report("主要工程量表", table)

    assert plan.layout == "metrics"
    assert plan.tables == []
    assert plan.bullets[:2] == ["120m：截水沟", "80根：锚杆"]


def test_schedule_table_becomes_timeline_plan():
    table = Table(
        headers=["节点", "计划时间", "责任人"],
        rows=[
            ["测量放样", "8月10日", "技术员"],
            ["边坡开挖", "8月12日", "施工班组"],
        ],
    )

    plan = plan_table_for_report("施工进度计划", table)

    assert plan.layout == "timeline"
    assert plan.bullets[0] == "8月10日：测量放样"


def test_small_table_is_kept_as_editable_table():
    table = Table(
        headers=["项目", "状态", "备注"],
        rows=[["图纸复核", "完成", "现场确认"], ["安全交底", "完成", "班组签字"]],
    )

    plan = plan_table_for_report("材料统计", table)

    assert plan.layout == "full-table"
    assert plan.tables == [table]


def test_wide_table_keeps_key_columns_only():
    table = Table(
        headers=["序号", "工程部位", "强度等级", "塌落度", "计划方量", "浇筑方式", "备注"],
        rows=[
            ["1", "洞口边坡", "C30", "180±30", "100", "泵送", "夜间"],
            ["2", "截水沟", "C20", "180±10", "12", "自卸", "白班"],
        ],
    )

    plan = plan_table_for_report("混凝土浇筑统计表", table)

    assert plan.layout == "metrics"
    assert plan.tables == []
    assert plan.bullets[0] == "100：洞口边坡"
