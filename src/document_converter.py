from pathlib import Path
import shutil
import subprocess


class DocumentConversionError(RuntimeError):
    pass


def convert_to_docx(source_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    for converter in (_convert_with_libreoffice, _convert_with_word):
        try:
            converted_path = converter(source_path, output_dir)
            if converted_path.exists():
                return converted_path
        except Exception:
            continue

    raise DocumentConversionError(
        "\u65e0\u6cd5\u81ea\u52a8\u8f6c\u6362\u8be5\u6587\u4ef6\u3002\u8bf7\u5b89\u88c5 LibreOffice\uff0c\u6216\u5728 WPS/Word \u4e2d\u5148\u5c06\u6587\u4ef6\u53e6\u5b58\u4e3a .docx \u540e\u518d\u4e0a\u4f20\u3002"
    )


def _convert_with_libreoffice(source_path: Path, output_dir: Path) -> Path:
    soffice_path = _find_soffice()
    if soffice_path is None:
        raise DocumentConversionError("LibreOffice not found.")

    command = [
        str(soffice_path),
        "--headless",
        "--convert-to",
        "docx",
        "--outdir",
        str(output_dir),
        str(source_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise DocumentConversionError(result.stderr or result.stdout)

    converted_path = output_dir / f"{source_path.stem}.docx"
    if not converted_path.exists():
        matches = list(output_dir.glob("*.docx"))
        if not matches:
            raise DocumentConversionError("LibreOffice did not create a docx file.")
        converted_path = matches[0]
    return converted_path


def _convert_with_word(source_path: Path, output_dir: Path) -> Path:
    try:
        import win32com.client
    except ImportError as exc:
        raise DocumentConversionError("pywin32 not installed.") from exc

    target_path = output_dir / f"{source_path.stem}.docx"
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    document = None
    try:
        document = word.Documents.Open(str(source_path))
        document.SaveAs(str(target_path), FileFormat=16)
    finally:
        if document is not None:
            document.Close(False)
        word.Quit()
    return target_path


def _find_soffice() -> Path | None:
    executable = shutil.which("soffice") or shutil.which("soffice.exe")
    if executable:
        return Path(executable)

    candidates = [
        Path("C:/Program Files/LibreOffice/program/soffice.exe"),
        Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None
