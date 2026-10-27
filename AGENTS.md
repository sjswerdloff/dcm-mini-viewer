# AGENTS.md — dcm-mini-viewer

A PySide6 + pydicom DICOM file viewer. **Medical software**: it reads and
displays DICOM datasets. Changes to dataset handling are changes to clinical
data — one cause at a time, verified against real files.

## Skills to load

- **medical-software-standards** — always; this is a DICOM viewer.
- **python-development**, **test-writing-philosophy**,
  **systematic-test-design** — before writing or reviewing code/tests.
- **linting-efficiency**, **development-tooling-efficiency** — for the
  tooling loops (ruff, JSON tool output, token-cheap CI reads).
- **code-graph** — before exploring the codebase (cross-file questions).
- **gitea-base**, plus the seat you are actually in:
  **gitea-branch-work** / **gitea-prs-landing** when developing,
  **gitea-review** when reviewing.

## Commands

- `uv sync --dev` — install.
- `uv run pytest` — run tests. With no display:
  `QT_QPA_PLATFORM=offscreen uv run pytest`.
- `uv run ruff check` and `uv run ruff format` — lint and format.
- **Never `pip`.** The environment belongs to uv (formerly Poetry); direct pip
  desynchronises it from the lock.

## Where work happens

- `dcm_mini_viewer/` — the package.
- `test/` — pytest tests.
- `.github/workflows/` — CI.
- `scripts/kindled_review_postcommit.sh` — post-commit review wrapper.

## Conventions

- Line length 127, enforced by ruff.
- Medical software: no silent failures. If a DICOM read fails, say so.
- One cause at a time. Tooling changes are tooling changes; behaviour changes
  are behaviour changes. Do not mix them.
