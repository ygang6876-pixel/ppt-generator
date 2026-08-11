# Contributing

Thank you for considering a contribution to PPT Generator. This project turns
Markdown, text outlines, office documents, images, Mermaid diagrams, and code
blocks into editable PowerPoint files.

## Good First Contributions

- Improve slide layouts and visual themes.
- Add regression tests for Markdown, docx, image, Mermaid, and API inputs.
- Improve document conversion behavior for `.doc` and `.wps` files.
- Improve upload validation and error messages.
- Add examples that show realistic document-to-slide workflows.

## Development Setup

```bash
pip install -r requirements.txt
npm install
```

Run the web app:

```bash
python app.py
```

Run the CLI:

```bash
python main.py inputs/example.md outputs/example.pptx
```

Run tests:

```bash
pytest
```

## Pull Request Guidelines

- Keep changes focused and explain the user-facing behavior.
- Add or update tests when changing parsing, generation, upload handling, or
  command execution behavior.
- Do not commit generated files from `outputs/`, local `.env` files, or
  credentials.
- Avoid adding network calls unless they are documented and optional.
- If a change invokes shell commands, document the command boundary and validate
  all user-controlled paths.

## Security-Sensitive Areas

Please be careful when changing:

- File upload and file name handling.
- Document conversion for `.doc`, `.wps`, and `.docx`.
- Mermaid rendering through local CLI tools or remote services.
- API endpoints that accept user-controlled content.
- Docker and dependency configuration.
