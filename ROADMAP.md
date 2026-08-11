# Roadmap

PPT Generator is maintained as a practical open source document-to-slide
automation tool.

## Near Term

- Add regression tests for Markdown, docx, image, Mermaid, code block, and API
  generation paths.
- Add GitHub Actions CI for Python tests and import checks.
- Improve upload validation, file size limits, and error messages.
- Add screenshots and generated deck examples to the README.

## Medium Term

- Improve long document splitting and slide overflow handling.
- Add more reusable visual templates.
- Add template previews in the web interface.
- Improve `.doc` and `.wps` conversion documentation and fallback behavior.

## Security Work

- Review path handling for uploaded files and Markdown image references.
- Review shell command boundaries for LibreOffice and Mermaid CLI.
- Make optional remote rendering behavior clear to users.
- Add dependency and Docker image checks in CI.

## Open Questions

- Whether to publish a packaged CLI.
- Whether to provide a hosted demo.
- Whether to add a plugin or agent workflow for automated document-to-PPT tasks.
