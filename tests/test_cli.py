import pytest

from task_tracker.cli import main


@pytest.fixture
def data_file(tmp_path):
    return str(tmp_path / "tasks.json")


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
