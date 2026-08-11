from io import BytesIO
import os
from pathlib import Path
import re
import tempfile

from flask import Flask, jsonify, render_template_string, request, send_file

from src.document_converter import DocumentConversionError, convert_to_docx
from src.docx_parser import parse_docx
from src.markdown_parser import Deck, ImageAsset, Slide, parse_markdown
from src.ppt_builder import build_presentation
from src.theme import get_theme


app = Flask(__name__)


TEXT = {
    "subtitle": "\u7c98\u8d34 Markdown\uff0c\u6216\u4e0a\u4f20 Markdown / WPS Word \u6587\u6863\uff0c\u751f\u6210\u53ef\u7f16\u8f91\u7684 PowerPoint\u3002",
    "markdown_label": "Markdown \u5185\u5bb9",
    "markdown_hint": "\u652f\u6301\u6807\u9898\u3001\u5217\u8868\u3001\u56fe\u7247\u8bed\u6cd5\u548c Markdown \u8868\u683c\uff1b\u4e0a\u4f20\u6587\u4ef6\u65f6\u4f1a\u4f18\u5148\u4f7f\u7528\u4e0a\u4f20\u6587\u4ef6\u3002",
    "upload_label": "\u4e0a\u4f20\u6587\u4ef6",
    "upload_hint": "\u652f\u6301 .md\u3001.txt\u3001.docx\uff0c\u5e76\u4f1a\u5c1d\u8bd5\u81ea\u52a8\u8f6c\u6362 .doc\u3001.wps\u3002",
    "image_upload_label": "\u4e0a\u4f20\u56fe\u7247",
    "image_upload_hint": "\u53ef\u591a\u9009\u56fe\u7247\u3002\u53ea\u4e0a\u4f20\u56fe\u7247\u65f6\uff0c\u6bcf\u5f20\u56fe\u7247\u751f\u6210\u4e00\u9875 PPT\u3002",
    "footer_label": "\u9875\u811a\u6587\u5b57",
    "output_label": "\u5bfc\u51fa\u6587\u4ef6\u540d",
    "output_hint": "\u4e0d\u7528\u8f93\u5165 .pptx \u540e\u7f00\uff0c\u7cfb\u7edf\u4f1a\u81ea\u52a8\u8865\u4e0a\u3002",
    "theme_label": "\u4e3b\u9898\u98ce\u683c",
    "button": "\u751f\u6210 PPT",
    "preview_button": "\u9884\u89c8\u7ed3\u6784",
    "preview_title": "\u751f\u6210\u9884\u89c8",
    "preview_hint": "\u8fd9\u91cc\u663e\u793a\u5373\u5c06\u751f\u6210\u7684 PPT \u7ed3\u6784\uff0c\u4fbf\u4e8e\u751f\u6210\u524d\u68c0\u67e5\u3002",
}


PAGE = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PPT Generator</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #69758a;
      --line: #d9dee7;
      --brand: #1f6feb;
      --brand-dark: #164fa8;
      --danger-bg: #fff1f2;
      --danger-line: #fecdd3;
      --danger-text: #9f1239;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    main {
      width: min(1080px, calc(100% - 32px));
      margin: 32px auto;
    }
    .top {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 20px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 34px;
      letter-spacing: 0;
    }
    .sub {
      margin: 0;
      color: var(--muted);
      font-size: 15px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 22px;
      box-shadow: 0 12px 30px rgba(23, 32, 51, 0.06);
    }
    .error {
      margin-bottom: 16px;
      padding: 12px 14px;
      border: 1px solid var(--danger-line);
      border-radius: 6px;
      background: var(--danger-bg);
      color: var(--danger-text);
      font-size: 14px;
    }
    .preview {
      margin-bottom: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfe;
      padding: 16px;
    }
    .preview h2 {
      margin: 0 0 6px;
      font-size: 20px;
      letter-spacing: 0;
    }
    .preview-summary {
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 14px;
    }
    .preview-list {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .preview-item {
      display: grid;
      grid-template-columns: 52px 1fr auto;
      gap: 12px;
      align-items: center;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }
    .preview-index {
      color: var(--muted);
      font-size: 13px;
    }
    .preview-name {
      font-weight: 700;
    }
    .preview-meta {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }
    form {
      display: grid;
      gap: 18px;
    }
    label {
      display: block;
      margin-bottom: 8px;
      color: #2d3748;
      font-weight: 600;
      font-size: 14px;
    }
    textarea, input[type="text"], input[type="file"], select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }
    textarea {
      min-height: 390px;
      padding: 14px;
      resize: vertical;
      line-height: 1.55;
      font-family: Consolas, "Microsoft YaHei", monospace;
    }
    input[type="text"], input[type="file"], select {
      min-height: 42px;
      padding: 8px 10px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .actions {
      display: flex;
      gap: 10px;
      justify-content: flex-end;
    }
    button {
      min-height: 44px;
      padding: 0 22px;
      border: 0;
      border-radius: 6px;
      background: var(--brand);
      color: #fff;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { background: var(--brand-dark); }
    .hint {
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
    }
    @media (max-width: 720px) {
      main { width: min(100% - 20px, 1080px); margin: 18px auto; }
      .top { display: block; }
      h1 { font-size: 28px; }
      .grid { grid-template-columns: 1fr; }
      textarea { min-height: 320px; }
    }
  </style>
</head>
<body>
  <main>
    <div class="top">
      <div>
        <h1>PPT Generator</h1>
        <p class="sub">{{ text.subtitle }}</p>
      </div>
    </div>
    <section class="panel">
      {% if error %}
        <div class="error">{{ error }}</div>
      {% endif %}
      {% if preview %}
        <div class="preview">
          <h2>{{ text.preview_title }}</h2>
          <div class="preview-summary">
            {{ text.preview_hint }} 标题：{{ preview.title }}；共 {{ preview.total_pages }} 页。
          </div>
          <ul class="preview-list">
            {% for item in preview.slides %}
              <li class="preview-item">
                <span class="preview-index">第 {{ item.index }} 页</span>
                <span class="preview-name">{{ item.title }}</span>
                <span class="preview-meta">{{ item.meta }}</span>
              </li>
            {% endfor %}
          </ul>
        </div>
      {% endif %}
      <form method="post" action="/generate" enctype="multipart/form-data">
        <div>
          <label for="content_text">{{ text.markdown_label }}</label>
          <textarea id="content_text" name="content_text">{{ sample }}</textarea>
          <div class="hint">{{ text.markdown_hint }}</div>
        </div>
        <div class="grid">
          <div>
            <label for="content_file">{{ text.upload_label }}</label>
            <input id="content_file" name="content_file" type="file" accept=".md,.markdown,.txt,.docx,.doc,.wps">
            <div class="hint">{{ text.upload_hint }}</div>
          </div>
          <div>
            <label for="image_files">{{ text.image_upload_label }}</label>
            <input id="image_files" name="image_files" type="file" accept=".png,.jpg,.jpeg,.webp,.bmp,.gif" multiple>
            <div class="hint">{{ text.image_upload_hint }}</div>
          </div>
        </div>
        <div class="grid">
          <div>
            <label for="footer">{{ text.footer_label }}</label>
            <input id="footer" name="footer" type="text" value="{{ footer }}">
          </div>
          <div>
            <label for="output_name">{{ text.output_label }}</label>
            <input id="output_name" name="output_name" type="text" value="{{ output_name }}">
            <div class="hint">{{ text.output_hint }}</div>
          </div>
          <div>
            <label for="theme">{{ text.theme_label }}</label>
            <select id="theme" name="theme">
              <option value="auto">按文档配置</option>
              <option value="business">Business</option>
              <option value="clean">Clean</option>
              <option value="dark">Dark</option>
              <option value="midnight">Midnight</option>
              <option value="emerald">Emerald</option>
              <option value="sunrise">Sunrise</option>
              <option value="ivory">Ivory</option>
              <option value="tech">Tech</option>
            </select>
          </div>
        </div>
        <div class="actions">
          <button type="submit" formaction="/preview">{{ text.preview_button }}</button>
          <button type="submit">{{ text.button }}</button>
        </div>
      </form>
    </section>
  </main>
</body>
</html>
"""


SAMPLE_MARKDOWN = """# PPT \u751f\u6210\u9879\u76ee\u6f14\u793a

\u6839\u636e Markdown \u6216 WPS \u6587\u6863\u81ea\u52a8\u751f\u6210 PowerPoint\u3002

## \u9879\u76ee\u76ee\u6807

- \u8f93\u5165 Markdown\u3001\u6587\u672c\u63d0\u7eb2\u6216 .docx \u6587\u6863
- \u81ea\u52a8\u62c6\u5206\u4e3a PPT \u9875\u9762
- \u751f\u6210\u53ef\u7f16\u8f91\u7684 `.pptx` \u6587\u4ef6

## \u529f\u80fd\u8fdb\u5ea6\u8868

| \u6a21\u5757 | \u72b6\u6001 | \u8bf4\u660e |
| --- | --- | --- |
| \u6807\u9898\u9875 | \u5df2\u5b8c\u6210 | \u81ea\u52a8\u751f\u6210\u5c01\u9762 |
| \u5185\u5bb9\u9875 | \u5df2\u5b8c\u6210 | \u652f\u6301\u6bb5\u843d\u548c\u5217\u8868 |
| \u8868\u683c\u9875 | \u5df2\u5b8c\u6210 | \u652f\u6301 Markdown \u548c Word \u8868\u683c |
"""


@app.get("/")
def index():
    return _render_page()


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.post("/generate")
def generate():
    uploaded_file = request.files.get("content_file") or request.files.get("markdown_file")
    image_files = [file for file in request.files.getlist("image_files") if file and file.filename]
    footer_text = request.form.get("footer") or "Generated by PPT Generator"
    output_name = _safe_output_name(request.form.get("output_name", "generated"))
    theme_name = request.form.get("theme")
    theme = None if theme_name in {None, "", "auto"} else get_theme(theme_name)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            deck, base_dir = _load_deck(uploaded_file, image_files, temp_path)
            output_path = temp_path / output_name
            build_presentation(deck, output_path, image_base_dir=base_dir, theme=theme, footer_text=footer_text)
            pptx_data = BytesIO(output_path.read_bytes())
            return send_file(
                pptx_data,
                as_attachment=True,
                download_name=output_name,
                mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
    except ValueError as exc:
        return _render_page(error=str(exc), status_code=400)
    except DocumentConversionError as exc:
        return _render_page(error=str(exc), status_code=400)
    except FileNotFoundError as exc:
        return _render_page(error=f"\u56fe\u7247\u6587\u4ef6\u672a\u627e\u5230\uff1a{exc}", status_code=400)


@app.post("/api/generate")
def api_generate():
    uploaded_file = request.files.get("content_file")
    image_files = [file for file in request.files.getlist("image_files") if file and file.filename]
    footer_text = request.form.get("footer") or "Generated by PPT Generator"
    output_name = _safe_output_name(request.form.get("output_name", "generated"))
    theme_name = request.form.get("theme")
    theme = None if theme_name in {None, "", "auto"} else get_theme(theme_name)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            deck, base_dir = _load_deck(uploaded_file, image_files, temp_path)
            output_path = temp_path / output_name
            build_presentation(deck, output_path, image_base_dir=base_dir, theme=theme, footer_text=footer_text)
            return send_file(
                BytesIO(output_path.read_bytes()),
                as_attachment=True,
                download_name=output_name,
                mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
    except (ValueError, DocumentConversionError, FileNotFoundError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/preview")
def preview():
    uploaded_file = request.files.get("content_file") or request.files.get("markdown_file")
    image_files = [file for file in request.files.getlist("image_files") if file and file.filename]

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            deck, _base_dir = _load_deck(uploaded_file, image_files, Path(temp_dir))
            return _render_page(preview=_preview_deck(deck))
    except ValueError as exc:
        return _render_page(error=str(exc), status_code=400)
    except DocumentConversionError as exc:
        return _render_page(error=str(exc), status_code=400)


@app.post("/api/preview")
def api_preview():
    uploaded_file = request.files.get("content_file")
    image_files = [file for file in request.files.getlist("image_files") if file and file.filename]
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            deck, _base_dir = _load_deck(uploaded_file, image_files, Path(temp_dir))
            return jsonify(_preview_deck(deck))
    except (ValueError, DocumentConversionError) as exc:
        return jsonify({"error": str(exc)}), 400


def _render_page(error: str | None = None, preview: dict | None = None, status_code: int = 200):
    return (
        render_template_string(
            PAGE,
            sample=SAMPLE_MARKDOWN,
            footer="\u6211\u7684PPT\u751f\u6210\u9879\u76ee",
            output_name="generated",
            error=error,
            preview=preview,
            text=TEXT,
        ),
        status_code,
    )


def _load_deck(uploaded_file, image_files, temp_path: Path):
    image_dir = temp_path / "images"
    saved_images = _save_images(image_files, image_dir)

    if uploaded_file and uploaded_file.filename:
        filename = Path(uploaded_file.filename)
        suffix = filename.suffix.lower()
        saved_path = temp_path / filename.name
        uploaded_file.save(saved_path)
        if suffix == ".docx":
            return parse_docx(saved_path), temp_path
        if suffix in {".doc", ".wps"}:
            converted_path = convert_to_docx(saved_path, temp_path)
            return parse_docx(converted_path), temp_path
        if suffix in {".md", ".markdown", ".txt"}:
            markdown_text = saved_path.read_text(encoding="utf-8-sig")
            _validate_text(markdown_text)
            return parse_markdown(markdown_text), temp_path
        raise ValueError("\u4ec5\u652f\u6301 .md\u3001.markdown\u3001.txt\u3001.docx\u3001.doc\u3001.wps \u6587\u4ef6\u3002")

    if saved_images:
        return _image_deck(saved_images), temp_path

    markdown_text = request.form.get("content_text") or request.form.get("markdown_text", "")
    _validate_text(markdown_text)
    return parse_markdown(markdown_text), Path.cwd()


def _validate_text(text: str) -> None:
    if not text.strip():
        raise ValueError("\u8bf7\u5148\u7c98\u8d34 Markdown \u5185\u5bb9\uff0c\u6216\u4e0a\u4f20\u4e00\u4e2a\u652f\u6301\u7684\u6587\u4ef6\u3002")


def _safe_output_name(name: str) -> str:
    stem = Path(name or "generated").stem
    stem = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]+", "_", stem).strip("_")
    if not stem:
        stem = "generated"
    return f"{stem}.pptx"


def _save_images(image_files, image_dir: Path) -> list[Path]:
    saved_paths: list[Path] = []
    if not image_files:
        return saved_paths
    image_dir.mkdir(parents=True, exist_ok=True)
    for image_file in image_files:
        filename = Path(image_file.filename)
        if filename.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}:
            raise ValueError("\u56fe\u7247\u4ec5\u652f\u6301 .png\u3001.jpg\u3001.jpeg\u3001.webp\u3001.bmp\u3001.gif \u683c\u5f0f\u3002")
        saved_path = image_dir / _safe_asset_name(filename.name)
        image_file.save(saved_path)
        saved_paths.append(saved_path)
    return saved_paths


def _image_deck(image_paths: list[Path]) -> Deck:
    slides = [
        Slide(
            title=image_path.stem,
            images=[ImageAsset(alt=image_path.stem, path=str(image_path.relative_to(image_path.parents[1])))],
            layout="image-full",
        )
        for image_path in image_paths
    ]
    return Deck(
        title="\u56fe\u7247\u6f14\u793a\u6587\u7a3f",
        subtitle="\u6839\u636e\u4e0a\u4f20\u56fe\u7247\u81ea\u52a8\u751f\u6210",
        slides=slides,
        metadata={"theme": "ivory", "footer": "PPT Generator"},
    )


def _safe_asset_name(name: str) -> str:
    path = Path(name)
    stem = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]+", "_", path.stem).strip("_") or "image"
    return f"{stem}{path.suffix.lower()}"


def _preview_deck(deck: Deck) -> dict:
    slides = [
        {"index": 1, "title": deck.title or "\u5c01\u9762", "meta": "\u5c01\u9762"}
    ]
    for index, slide in enumerate(deck.slides, start=2):
        text_count = len(slide.body) + len(slide.bullets)
        meta_parts = [f"\u5e03\u5c40 {slide.layout}"]
        if text_count:
            meta_parts.append(f"\u6587\u5b57 {text_count}")
        if slide.images:
            meta_parts.append(f"\u56fe\u7247 {len(slide.images)}")
        if slide.tables:
            meta_parts.append(f"\u8868\u683c {len(slide.tables)}")
        if slide.mermaid:
            meta_parts.append(f"Mermaid {len(slide.mermaid)}")
        if slide.code_blocks:
            meta_parts.append(f"\u4ee3\u7801 {len(slide.code_blocks)}")
        slides.append(
            {
                "index": index,
                "title": slide.title or "\u672a\u547d\u540d",
                "meta": " / ".join(meta_parts),
            }
        )
    return {"title": deck.title, "total_pages": len(slides), "slides": slides}


if __name__ == "__main__":
    host = os.environ.get("PPT_GENERATOR_HOST", "127.0.0.1")
    port = int(os.environ.get("PPT_GENERATOR_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
