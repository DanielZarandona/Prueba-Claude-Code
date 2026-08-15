import pytest

from task_tracker.storage import TaskStorage


@pytest.fixture
def storage(tmp_path):
    return TaskStorage(tmp_path / "tasks.json")


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


def test_next_id_is_based_on_max_remaining_id(storage):
    storage.add("Tarea 1")
    second = storage.add("Tarea 2")
    storage.delete(second.id)

    third = storage.add("Tarea 3")

    assert third.id == 2
