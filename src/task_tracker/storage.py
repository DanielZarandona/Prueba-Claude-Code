"""Persistencia de tareas en una base de datos SQLite local (`TaskStorage`).

Cada operación abre y cierra su propia conexión a la base; no se mantiene
un handle persistente entre invocaciones de la CLI. Los ids se asignan como
`MAX(id) + 1` (en vez de `AUTOINCREMENT`) para preservar el comportamiento
histórico de reutilizar el id de una tarea eliminada.
"""

import csv
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional

from task_tracker.models import Task

CSV_FIELDS = ["id", "title", "done", "created_at", "priority"]

DEFAULT_DATA_PATH = Path("data") / "tasks.db"

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    done INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    priority TEXT NOT NULL
)
"""


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        done=bool(row["done"]),
        created_at=row["created_at"],
        priority=row["priority"],
    )


class TaskStorage:
    """Persiste tareas en una base de datos SQLite local."""

    def __init__(self, path: Path = DEFAULT_DATA_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE_SQL)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def load(self) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [_row_to_task(row) for row in rows]

    def add(self, title: str, priority: str = "media") -> Task:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            next_id = (conn.execute("SELECT MAX(id) FROM tasks").fetchone()[0] or 0) + 1
            task = Task(id=next_id, title=title, priority=priority)
            conn.execute(
                "INSERT INTO tasks (id, title, done, created_at, priority) "
                "VALUES (?, ?, ?, ?, ?)",
                (task.id, task.title, int(task.done), task.created_at, task.priority),
            )
        return task

    def list(self) -> List[Task]:
        return self.load()

    def list_high_priority(self) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE priority = 'alta' ORDER BY id"
            ).fetchall()
        return [_row_to_task(row) for row in rows]

    def complete(self, task_id: int) -> Task:
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE tasks SET done = 1 WHERE id = ?", (task_id,)
            )
            if cursor.rowcount == 0:
                raise ValueError(f"No existe una tarea con id {task_id}")
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_task(row)

    def delete(self, task_id: int) -> Task:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount == 0:
                raise ValueError(f"No existe una tarea con id {task_id}")
        return _row_to_task(row)

    def export_csv(self, output_path: Path) -> int:
        output_path = Path(output_path)
        tasks = self.load()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for task in tasks:
                writer.writerow(task.to_dict())
        return len(tasks)

    def import_from_json(self, json_path: Path, *, force: bool = False) -> int:
        json_path = Path(json_path)
        if not json_path.exists():
            raise ValueError(f"No se encontró el archivo JSON: {json_path}")

        with json_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        tasks = [Task.from_dict(item) for item in raw]

        with self._connect() as conn:
            existing_count: Optional[int] = conn.execute(
                "SELECT COUNT(*) FROM tasks"
            ).fetchone()[0]
            if existing_count and not force:
                raise ValueError(
                    "La base de datos ya contiene tareas; use --force para sobrescribir."
                )
            conn.execute("DELETE FROM tasks")
            try:
                conn.executemany(
                    "INSERT INTO tasks (id, title, done, created_at, priority) "
                    "VALUES (?, ?, ?, ?, ?)",
                    [
                        (task.id, task.title, int(task.done), task.created_at, task.priority)
                        for task in tasks
                    ],
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(
                    f"El archivo JSON tiene ids de tarea duplicados: {exc}"
                ) from exc
        return len(tasks)
