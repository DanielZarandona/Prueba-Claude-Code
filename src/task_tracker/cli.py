import argparse
import sys
from typing import List, Optional

from task_tracker.models import PRIORITIES, Task
from task_tracker.storage import DEFAULT_DATA_PATH, TaskStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-tracker",
        description="CLI simple para gestionar tareas guardadas en una base de datos SQLite local.",
    )
    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA_PATH),
        help="Ruta a la base de datos SQLite de tareas (por defecto: ./data/tasks.db)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Agregar una nueva tarea")
    add_parser.add_argument("title", help="Título de la tarea")
    add_parser.add_argument(
        "--prioridad",
        dest="priority",
        choices=PRIORITIES,
        default="media",
        help="Prioridad de la tarea (por defecto: media)",
    )

    subparsers.add_parser("list", help="Listar todas las tareas")

    subparsers.add_parser(
        "list-high", help="Listar solo las tareas de prioridad alta"
    )

    complete_parser = subparsers.add_parser(
        "complete", help="Marcar una tarea como completada"
    )
    complete_parser.add_argument("id", type=int, help="ID de la tarea")

    delete_parser = subparsers.add_parser("delete", help="Eliminar una tarea")
    delete_parser.add_argument("id", type=int, help="ID de la tarea")

    export_parser = subparsers.add_parser(
        "export", help="Exportar las tareas a un archivo CSV"
    )
    export_parser.add_argument(
        "output",
        nargs="?",
        default="tasks.csv",
        help="Ruta del archivo CSV de salida (por defecto: tasks.csv)",
    )

    migrate_parser = subparsers.add_parser(
        "migrate-from-json",
        help="Importar tareas desde un archivo JSON (formato de versiones anteriores)",
    )
    migrate_parser.add_argument("json_path", help="Ruta al archivo JSON a importar")
    migrate_parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribir las tareas existentes en la base de datos, si las hay",
    )

    return parser


def format_task(task: Task) -> str:
    status = "x" if task.done else " "
    return f"[{status}] #{task.id} {task.title} ({task.priority})"


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = TaskStorage(args.data)

    if args.command == "add":
        # Crea una tarea nueva con el título y la prioridad indicados (o "media" por defecto).
        task = storage.add(args.title, priority=args.priority)
        print(f"Tarea agregada: {format_task(task)}")
        return 0

    if args.command == "list":
        # Lista todas las tareas guardadas, sin filtrar por prioridad ni estado.
        tasks = storage.list()
        if not tasks:
            print("No hay tareas.")
        else:
            for task in tasks:
                print(format_task(task))
        return 0

    if args.command == "list-high":
        # Lista únicamente las tareas cuya prioridad es "alta".
        tasks = storage.list_high_priority()
        if not tasks:
            print("No hay tareas de prioridad alta.")
        else:
            for task in tasks:
                print(format_task(task))
        return 0

    if args.command == "complete":
        # Marca como completada la tarea con el id indicado.
        try:
            task = storage.complete(args.id)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Tarea completada: {format_task(task)}")
        return 0

    if args.command == "delete":
        # Elimina la tarea con el id indicado.
        try:
            task = storage.delete(args.id)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Tarea eliminada: {format_task(task)}")
        return 0

    if args.command == "export":
        # Exporta todas las tareas (con su prioridad) a un archivo CSV en args.output.
        count = storage.export_csv(args.output)
        print(f"{count} tarea(s) exportada(s) a {args.output}")
        return 0

    if args.command == "migrate-from-json":
        # Importa tareas desde un archivo JSON (formato usado antes de migrar a SQLite).
        try:
            count = storage.import_from_json(args.json_path, force=args.force)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"{count} tarea(s) importada(s) desde {args.json_path}.")
        return 0

    parser.error(f"Comando desconocido: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
