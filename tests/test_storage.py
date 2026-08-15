import json
import sqlite3

import pytest

from task_tracker.storage import TaskStorage


@pytest.fixture
def storage(tmp_path):
    return TaskStorage(tmp_path / "tasks.db")


def test_load_returns_empty_list_when_file_missing(storage):
    assert storage.load() == []


def test_add_creates_task_with_incremental_id(storage):
    first = storage.add("Comprar leche")
    second = storage.add("Pagar factura")

    assert first.id == 1
    assert second.id == 2
    assert first.done is False


def test_add_defaults_to_media_priority(storage):
    task = storage.add("Comprar leche")

    assert task.priority == "media"


def test_add_accepts_explicit_priority(storage):
    task = storage.add("Comprar leche", priority="alta")

    assert task.priority == "alta"


def test_add_rejects_invalid_priority(storage):
    with pytest.raises(ValueError):
        storage.add("Comprar leche", priority="urgente")


def test_list_high_priority_returns_only_alta_tasks(storage):
    storage.add("Tarea alta", priority="alta")
    storage.add("Tarea media", priority="media")
    storage.add("Tarea baja", priority="baja")

    high = storage.list_high_priority()

    assert len(high) == 1
    assert high[0].title == "Tarea alta"


def test_add_persists_to_json_file(storage):
    storage.add("Comprar leche")

    reloaded = TaskStorage(storage.path)
    tasks = reloaded.list()

    assert len(tasks) == 1
    assert tasks[0].title == "Comprar leche"


def test_complete_marks_task_as_done(storage):
    task = storage.add("Comprar leche")

    completed = storage.complete(task.id)

    assert completed.done is True
    assert storage.list()[0].done is True


def test_complete_raises_for_unknown_id(storage):
    with pytest.raises(ValueError):
        storage.complete(999)


def test_delete_removes_task(storage):
    task = storage.add("Comprar leche")

    removed = storage.delete(task.id)

    assert removed.id == task.id
    assert storage.list() == []


def test_delete_raises_for_unknown_id(storage):
    with pytest.raises(ValueError):
        storage.delete(999)


def test_delete_raises_when_row_disappears_between_select_and_delete(storage, monkeypatch):
    """delete() debe basar el "no existe" en el rowcount del propio DELETE,
    no en el SELECT previo, para no reportar éxito si la fila ya no está
    presente en el momento de borrar (p.ej. otra conexión la eliminó en la
    ventana entre ambas sentencias)."""
    task = storage.add("Comprar leche")
    original_connect = sqlite3.connect

    class RacingConnection(sqlite3.Connection):
        triggered = False

        def execute(self, sql, *args, **kwargs):
            result = super().execute(sql, *args, **kwargs)
            if not self.triggered and sql.strip().startswith(
                "SELECT * FROM tasks WHERE id"
            ):
                self.triggered = True
                super().execute("DELETE FROM tasks WHERE id = ?", (task.id,))
            return result

    def connect_with_race(*args, **kwargs):
        kwargs.setdefault("factory", RacingConnection)
        return original_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", connect_with_race)

    with pytest.raises(ValueError):
        storage.delete(task.id)


def test_next_id_is_based_on_max_remaining_id(storage):
    storage.add("Tarea 1")
    second = storage.add("Tarea 2")
    storage.delete(second.id)

    third = storage.add("Tarea 3")

    assert third.id == 2


def test_export_csv_writes_header_and_rows(storage, tmp_path):
    storage.add("Comprar leche", priority="alta")
    storage.add("Pagar factura")
    csv_path = tmp_path / "export" / "tareas.csv"

    count = storage.export_csv(csv_path)

    assert count == 2
    content = csv_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    assert lines[0] == "id,title,done,created_at,priority"
    assert "Comprar leche" in content
    assert "alta" in content
    assert "Pagar factura" in content


def test_export_csv_writes_only_header_when_no_tasks(storage, tmp_path):
    csv_path = tmp_path / "tareas.csv"

    count = storage.export_csv(csv_path)

    assert count == 0
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines == ["id,title,done,created_at,priority"]


def _write_json_tasks(path, tasks):
    with path.open("w", encoding="utf-8") as f:
        json.dump(tasks, f)


def test_import_from_json_loads_tasks_into_empty_db(storage, tmp_path):
    json_path = tmp_path / "tasks.json"
    _write_json_tasks(
        json_path,
        [
            {
                "id": 1,
                "title": "Comprar leche",
                "done": False,
                "created_at": "2024-01-01T00:00:00",
                "priority": "alta",
            }
        ],
    )

    count = storage.import_from_json(json_path)

    assert count == 1
    tasks = storage.list()
    assert len(tasks) == 1
    assert tasks[0].title == "Comprar leche"
    assert tasks[0].priority == "alta"


def test_import_from_json_raises_when_file_missing(storage, tmp_path):
    with pytest.raises(ValueError):
        storage.import_from_json(tmp_path / "no_existe.json")


def test_import_from_json_raises_when_db_already_has_tasks(storage, tmp_path):
    storage.add("Tarea existente")
    json_path = tmp_path / "tasks.json"
    _write_json_tasks(json_path, [])

    with pytest.raises(ValueError):
        storage.import_from_json(json_path)


def test_import_from_json_raises_for_duplicate_ids(storage, tmp_path):
    json_path = tmp_path / "tasks.json"
    _write_json_tasks(
        json_path,
        [
            {
                "id": 1,
                "title": "Tarea 1",
                "done": False,
                "created_at": "2024-01-01T00:00:00",
                "priority": "media",
            },
            {
                "id": 1,
                "title": "Tarea 1 duplicada",
                "done": False,
                "created_at": "2024-01-01T00:00:00",
                "priority": "alta",
            },
        ],
    )

    with pytest.raises(ValueError):
        storage.import_from_json(json_path)

    assert storage.list() == []


def test_import_from_json_with_force_overwrites_existing_tasks(storage, tmp_path):
    storage.add("Tarea existente")
    json_path = tmp_path / "tasks.json"
    _write_json_tasks(
        json_path,
        [
            {
                "id": 1,
                "title": "Tarea importada",
                "done": False,
                "created_at": "2024-01-01T00:00:00",
                "priority": "media",
            }
        ],
    )

    count = storage.import_from_json(json_path, force=True)

    assert count == 1
    tasks = storage.list()
    assert len(tasks) == 1
    assert tasks[0].title == "Tarea importada"
