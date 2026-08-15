import argparse
import sys
from typing import List, Optional

from task_tracker.models import Task
from task_tracker.storage import DEFAULT_DATA_PATH, TaskStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-tracker",
        description="CLI simple para gestionar tareas guardadas en un archivo JSON local.",
    )
    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA_PATH),
        help="Ruta al archivo JSON de tareas (por defecto: ./data/tasks.json)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Agregar una nueva tarea")
    add_parser.add_argument("title", help="Título de la tarea")

    subparsers.add_parser("list", help="Listar todas las tareas")

    complete_parser = subparsers.add_parser(
        "complete", help="Marcar una tarea como completada"
    )
    complete_parser.add_argument("id", type=int, help="ID de la tarea")

    delete_parser = subparsers.add_parser("delete", help="Eliminar una tarea")
    delete_parser.add_argument("id", type=int, help="ID de la tarea")

    return parser


def format_task(task: Task) -> str:
    status = "x" if task.done else " "
    return f"[{status}] #{task.id} {task.title}"


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = TaskStorage(args.data)

    if args.command == "add":
        task = storage.add(args.title)
        print(f"Tarea agregada: {format_task(task)}")
        return 0

    if args.command == "list":
        tasks = storage.list()
        if not tasks:
            print("No hay tareas.")
        else:
            for task in tasks:
                print(format_task(task))
        return 0

    if args.command == "complete":
        try:
            task = storage.complete(args.id)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Tarea completada: {format_task(task)}")
        return 0

    if args.command == "delete":
        try:
            task = storage.delete(args.id)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Tarea eliminada: {format_task(task)}")
        return 0

    parser.error(f"Comando desconocido: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
