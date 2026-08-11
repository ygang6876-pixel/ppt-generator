from pathlib import Path
import hashlib
import shutil
import subprocess
import urllib.request


class MermaidRenderError(RuntimeError):
    pass


def render_mermaid(code: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(code.encode("utf-8")).hexdigest()[:12]
    output_path = output_dir / f"mermaid_{digest}.png"
    if output_path.exists():
        return output_path

    try:
        return _render_with_mmdc(code, output_path)
    except MermaidRenderError:
        pass

    try:
        return _render_with_kroki(code, output_path)
    except MermaidRenderError as exc:
        raise MermaidRenderError(
            "Mermaid 图表渲染失败。请检查 Mermaid 语法，或安装 @mermaid-js/mermaid-cli 后重试。"
        ) from exc


def _render_with_mmdc(code: str, output_path: Path) -> Path:
    mmdc = _find_mmdc()
    if mmdc is None:
        raise MermaidRenderError("mmdc not found.")

    source_path = output_path.with_suffix(".mmd")
    source_path.write_text(code, encoding="utf-8")
    command = [mmdc, "-i", str(source_path), "-o", str(output_path), "-b", "transparent"]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode != 0 or not output_path.exists():
        raise MermaidRenderError(result.stderr or result.stdout)
    return output_path


def _find_mmdc() -> str | None:
    local_bin = Path.cwd() / "node_modules" / ".bin"
    candidates = [
        local_bin / "mmdc.cmd",
        local_bin / "mmdc",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return shutil.which("mmdc") or shutil.which("mmdc.cmd")


def _render_with_kroki(code: str, output_path: Path) -> Path:
    request = urllib.request.Request(
        "https://kroki.io/mermaid/png",
        data=code.encode("utf-8"),
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "image/png",
            "User-Agent": "ppt-generator/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            output_path.write_bytes(response.read())
    except Exception as exc:
        raise MermaidRenderError(str(exc)) from exc

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise MermaidRenderError("Kroki returned an empty image.")
    return output_path
