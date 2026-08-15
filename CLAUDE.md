# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`task-tracker` is a simple Python CLI for managing tasks (add/list/complete/delete) stored in a local JSON file (`./data/tasks.json` by default).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
pip install -r requirements.txt
```

## Commands

- Run the CLI: `task-tracker <add|list|complete|delete> ...` or `python -m task_tracker ...`
- Use a custom data file: `task-tracker --data otra_ruta/tasks.json list`
- Run all tests: `pytest`
- Run a single test file: `pytest tests/test_storage.py`
- Run a single test: `pytest tests/test_storage.py::test_add_creates_task_with_incremental_id`

## Architecture

- `src/task_tracker/models.py` — `Task` dataclass (id, title, done, created_at).
- `src/task_tracker/storage.py` — `TaskStorage` handles all JSON persistence. Every operation (`add`/`complete`/`delete`) reads the *entire* task list from disk, mutates it in memory, and rewrites the whole file — there is no incremental/partial write, so this isn't suited for large lists or concurrent access.
- `src/task_tracker/cli.py` — argparse-based CLI wiring (`add`/`list`/`complete`/`delete` subcommands) and the `main()` entry point exposed as the `task-tracker` console script.
- `src/task_tracker/__main__.py` — enables `python -m task_tracker`.
- Task IDs are assigned as `max(existing ids) + 1`; deleting the task with the current highest id frees that id for reuse by the next `add`.
- `pyproject.toml` sets `pythonpath = ["src"]` for pytest, so tests can `import task_tracker` without needing the editable install.

## CI

`.github/workflows/tests.yml` runs `pytest` on Python 3.9 and 3.12 on every push/PR to any branch. The README's "Tests" badge reflects the latest run on `main`.

## Notes

- User-facing CLI strings and the README are written in Spanish; keep new user-facing text and error messages consistent with that.
