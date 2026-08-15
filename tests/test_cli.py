import json
from pathlib import Path

import pytest

from task_tracker.cli import main


@pytest.fixture
def data_file(tmp_path):
    return str(tmp_path / "tasks.db")


def test_add_prints_confirmation(capsys, data_file):
    exit_code = main(["--data", data_file, "add", "Comprar leche"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tarea agregada" in captured.out
    assert "Comprar leche" in captured.out


def test_list_shows_no_tasks_message_when_empty(capsys, data_file):
    exit_code = main(["--data", data_file, "list"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No hay tareas." in captured.out


def test_list_shows_added_tasks(capsys, data_file):
    main(["--data", data_file, "add", "Comprar leche"])
    main(["--data", data_file, "add", "Pagar factura"])
    capsys.readouterr()

    exit_code = main(["--data", data_file, "list"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Comprar leche" in captured.out
    assert "Pagar factura" in captured.out


def test_add_with_priority_shows_it_in_confirmation(capsys, data_file):
    exit_code = main(["--data", data_file, "add", "Comprar leche", "--prioridad", "alta"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "(alta)" in captured.out


def test_list_high_shows_only_high_priority_tasks(capsys, data_file):
    main(["--data", data_file, "add", "Tarea urgente", "--prioridad", "alta"])
    main(["--data", data_file, "add", "Tarea normal", "--prioridad", "media"])
    capsys.readouterr()

    exit_code = main(["--data", data_file, "list-high"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tarea urgente" in captured.out
    assert "Tarea normal" not in captured.out


def test_list_high_shows_no_tasks_message_when_empty(capsys, data_file):
    exit_code = main(["--data", data_file, "list-high"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No hay tareas de prioridad alta." in captured.out


def test_complete_marks_task_as_done(capsys, data_file):
    main(["--data", data_file, "add", "Comprar leche"])
    capsys.readouterr()

    exit_code = main(["--data", data_file, "complete", "1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tarea completada" in captured.out
    assert "[x]" in captured.out


def test_complete_unknown_id_returns_error(capsys, data_file):
    exit_code = main(["--data", data_file, "complete", "42"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No existe una tarea" in captured.err


def test_delete_removes_task(capsys, data_file):
    main(["--data", data_file, "add", "Comprar leche"])
    capsys.readouterr()

    exit_code = main(["--data", data_file, "delete", "1"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tarea eliminada" in captured.out

    main(["--data", data_file, "list"])
    list_output = capsys.readouterr()
    assert "No hay tareas." in list_output.out


def test_delete_unknown_id_returns_error(capsys, data_file):
    exit_code = main(["--data", data_file, "delete", "42"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No existe una tarea" in captured.err


def test_export_writes_csv_file(capsys, data_file, tmp_path):
    main(["--data", data_file, "add", "Comprar leche", "--prioridad", "alta"])
    capsys.readouterr()

    csv_path = str(tmp_path / "tareas.csv")
    exit_code = main(["--data", data_file, "export", csv_path])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "1 tarea(s) exportada(s)" in captured.out

    content = Path(csv_path).read_text(encoding="utf-8")
    assert "Comprar leche" in content
    assert "alta" in content


def test_migrate_from_json_imports_tasks(capsys, data_file, tmp_path):
    json_path = tmp_path / "old_tasks.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "id": 1,
                    "title": "Tarea vieja",
                    "done": False,
                    "created_at": "2024-01-01T00:00:00",
                    "priority": "alta",
                }
            ],
            f,
        )

    exit_code = main(["--data", data_file, "migrate-from-json", str(json_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "1 tarea(s) importada(s)" in captured.out

    main(["--data", data_file, "list"])
    list_output = capsys.readouterr()
    assert "Tarea vieja" in list_output.out


def test_migrate_from_json_missing_file_returns_error(capsys, data_file, tmp_path):
    json_path = tmp_path / "no_existe.json"

    exit_code = main(["--data", data_file, "migrate-from-json", str(json_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No se encontró el archivo JSON" in captured.err


def test_migrate_from_json_refuses_to_overwrite_without_force(capsys, data_file, tmp_path):
    main(["--data", data_file, "add", "Tarea existente"])
    capsys.readouterr()

    json_path = tmp_path / "old_tasks.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump([], f)

    exit_code = main(["--data", data_file, "migrate-from-json", str(json_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "--force" in captured.err
