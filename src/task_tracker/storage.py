import json
from pathlib import Path
from typing import List

from task_tracker.models import Task

DEFAULT_DATA_PATH = Path("data") / "tasks.json"


class TaskStorage:
    """Persiste tareas en un archivo JSON local."""

    def __init__(self, path: Path = DEFAULT_DATA_PATH):
        self.path = Path(path)

    def load(self) -> List[Task]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Task.from_dict(item) for item in raw]

    def save(self, tasks: List[Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2, ensure_ascii=False)

    def add(self, title: str) -> Task:
        tasks = self.load()
        next_id = max((t.id for t in tasks), default=0) + 1
        task = Task(id=next_id, title=title)
        tasks.append(task)
        self.save(tasks)
        return task

    def list(self) -> List[Task]:
        return self.load()

    def complete(self, task_id: int) -> Task:
        tasks = self.load()
        for task in tasks:
            if task.id == task_id:
                task.done = True
                self.save(tasks)
                return task
        raise ValueError(f"No existe una tarea con id {task_id}")

    def delete(self, task_id: int) -> Task:
        tasks = self.load()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                removed = tasks.pop(index)
                self.save(tasks)
                return removed
        raise ValueError(f"No existe una tarea con id {task_id}")
