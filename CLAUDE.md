# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`task-tracker` is a simple Python CLI for managing tasks (add/list/complete/delete) stored in a local SQLite database (`./data/tasks.db` by default).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
pip install -r requirements.txt
```

## Commands

- Run the CLI: `task-tracker <add|list|complete|delete> ...` or `python -m task_tracker ...`
- Use a custom data file: `task-tracker --data otra_ruta/tasks.db list`
- Import tasks from a legacy JSON file: `task-tracker migrate-from-json tasks.json [--force]`
- Run all tests: `pytest`
- Run a single test file: `pytest tests/test_storage.py`
- Run a single test: `pytest tests/test_storage.py::test_add_creates_task_with_incremental_id`

## Architecture

- `src/task_tracker/models.py` — `Task` dataclass (id, title, done, created_at).
- `src/task_tracker/storage.py` — `TaskStorage` handles all persistence via stdlib `sqlite3` (no ORM). Each operation opens and closes its own connection; there is no long-lived connection held between CLI invocations. Task ids are assigned as `MAX(id) + 1` in an explicit transaction rather than `AUTOINCREMENT`, to preserve id reuse after deletes (see below). `import_from_json` migrates a legacy JSON file into the database, refusing to overwrite existing tasks unless `force=True`.
- `src/task_tracker/cli.py` — argparse-based CLI wiring (`add`/`list`/`list-high`/`complete`/`delete`/`export`/`migrate-from-json` subcommands) and the `main()` entry point exposed as the `task-tracker` console script.
- `src/task_tracker/__main__.py` — enables `python -m task_tracker`.
- Task IDs are assigned as `max(existing ids) + 1`; deleting the task with the current highest id frees that id for reuse by the next `add`.
- `pyproject.toml` sets `pythonpath = ["src"]` for pytest, so tests can `import task_tracker` without needing the editable install.

## CI

`.github/workflows/tests.yml` runs `pytest` on Python 3.9 and 3.12 on every push/PR to any branch. The README's "Tests" badge reflects the latest run on `main`.

## Notes

- User-facing CLI strings and the README are written in Spanish; keep new user-facing text and error messages consistent with that.
- Use type hints on all functions.
- Commit messages must follow Conventional Commits.
