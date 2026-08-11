# Security Policy

## Supported Versions

This repository is early-stage. Security fixes are applied to the `main` branch.

## Reporting a Vulnerability

Please report security issues by opening a private report if GitHub private
vulnerability reporting is enabled, or by contacting the maintainer through the
GitHub profile linked from this repository.

Please include:

- A short description of the issue.
- A minimal reproduction case.
- The affected file type or API endpoint.
- Whether the issue requires local access, uploaded content, or network access.

## Current Security Model

PPT Generator processes user-controlled content, including Markdown, office
documents, images, Mermaid diagrams, and API form data. The main risks are:

- Malicious uploaded files.
- Path traversal through uploaded file names or image references.
- Markdown or diagram content that triggers unsafe rendering behavior.
- Shell command boundaries around LibreOffice and Mermaid CLI execution.
- Optional remote rendering through Kroki.
- Dependency and Docker image supply-chain risks.

## Maintainer Priorities

- Keep generated files isolated from source files.
- Validate supported extensions before processing.
- Avoid exposing credentials through logs, examples, or environment files.
- Keep network calls documented and optional where possible.
- Review third-party contributions that touch file handling, shell execution,
  API inputs, or dependency configuration.
