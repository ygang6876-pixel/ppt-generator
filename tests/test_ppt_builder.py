from pathlib import Path

from pptx import Presentation

from src.markdown_parser import Deck, Slide
from src.ppt_builder import build_presentation
from src.theme import get_theme


def test_semantic_design_layouts_render(tmp_path: Path):
    deck = Deck(
        title="施工方案汇报",
        subtitle="设计引擎测试",
        slides=[
            Slide(title="汇报重点", bullets=["高边坡开挖支护属于重点风险控制内容"], layout="highlight"),
            Slide(title="汇报目录", bullets=["工程概况", "施工部署", "风险控制"], layout="agenda"),
            Slide(title="工程概况", body=["洞口高边坡开挖支护，包含截水沟、防护网、锚喷支护。"], layout="overview"),
            Slide(title="施工工艺流程", bullets=["测量放样", "开挖", "支护", "验收"], layout="process"),
            Slide(title="风险辨识与控制", bullets=["边坡坍塌", "物体打击", "触电伤害"], layout="risk"),
            Slide(title="安全保障措施", bullets=["交底到位", "专人检查", "闭环整改"], layout="checklist"),
        ],
    )
    output_path = tmp_path / "semantic.pptx"

    build_presentation(deck, output_path, theme=get_theme("construction"))

    prs = Presentation(output_path)
    assert len(prs.slides) == 7
    assert output_path.stat().st_size > 0
