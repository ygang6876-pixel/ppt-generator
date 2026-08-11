from src.content_distiller import distill_slide_items, summarize_table_for_report


def test_distills_process_into_short_steps():
    body, bullets = distill_slide_items(
        "施工工艺流程",
        [],
        ["测量放样→分层开挖→锚喷支护→检查验收→资料归档"],
        "process",
    )

    assert body == []
    assert bullets == ["测量放样", "分层开挖", "锚喷支护", "检查验收"]


def test_distills_risk_slide_into_labeled_items():
    body, bullets = distill_slide_items(
        "风险辨识与控制",
        ["边坡开挖期间必须控制临边坠落和危石滚落风险，作业前应完成安全交底。"],
        ["现场应安排专人检查防护设施，发现隐患不得继续作业。"],
        "risk",
    )

    assert body == []
    assert bullets[0].startswith("风险点：")
    assert bullets[1].startswith("控制措施：")
    assert all(len(item) <= 48 for item in bullets)


def test_summarizes_complex_table_for_report():
    body, bullets = summarize_table_for_report(
        ["序号", "工程部位", "强度等级", "塌落度", "计划方量", "浇筑方式"],
        [
            ["1", "洞口边坡", "C30", "180±30", "100", "泵送"],
            ["2", "截水沟", "C20", "180±10", "12", "自卸"],
        ],
    )

    assert body == ["源表格共 2 行、6 列；汇报版提取字段和代表项，避免压缩失真。"]
    assert bullets[0] == "字段：序号、工程部位、强度等级、塌落度、计划方量"
    assert bullets[1] == "1 / 洞口边坡 / C30"
