# task-tracker

[![Tests](https://github.com/DanielZarandona/Prueba-Claude-Code/actions/workflows/tests.yml/badge.svg)](https://github.com/DanielZarandona/Prueba-Claude-Code/actions/workflows/tests.yml)

CLI simple para gestionar tareas (agregar, listar, completar, eliminar),
guardadas en una base de datos SQLite local en `./data/tasks.db`.

## Estructura del proyecto

```
task-tracker/
├── src/
│   └── task_tracker/
│       ├── __init__.py
│       ├── __main__.py   # permite `python -m task_tracker`
│       ├── cli.py         # parseo de argumentos y comandos
│       ├── models.py      # modelo Task
│       └── storage.py     # persistencia en SQLite
├── tests/
│   ├── test_cli.py
│   └── test_storage.py
├── data/
│   └── tasks.db             # se crea automáticamente al agregar la primera tarea
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Instalación

Se recomienda usar un entorno virtual.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -e .
pip install -r requirements.txt
```

## Uso

Una vez instalado, el comando `task-tracker` queda disponible. También puede
ejecutarse como módulo con `python -m task_tracker`.

```bash
# Agregar una tarea
task-tracker add "Comprar leche"

# Listar todas las tareas
task-tracker list

# Marcar una tarea como completada (usando su id)
task-tracker complete 1

# Eliminar una tarea
task-tracker delete 1

# Exportar las tareas a CSV (por defecto: tasks.csv)
task-tracker export
task-tracker export mis_tareas.csv

# Importar tareas desde un archivo JSON de una versión anterior
task-tracker migrate-from-json tasks_viejas.json
task-tracker migrate-from-json tasks_viejas.json --force  # sobrescribe si ya hay tareas
```

Por defecto las tareas se guardan en `./data/tasks.db` (relativo al
directorio desde el que se ejecuta el comando). Puede usarse otra ruta con
`--data`:

```bash
task-tracker --data otra_ruta/tasks.db list
```

## Tests

```bash
pip install -r requirements.txt
pytest
```

## Integración continua

El badge "Tests" al inicio de este README refleja el resultado del último
workflow de GitHub Actions (`.github/workflows/tests.yml`) ejecutado sobre
`main`. Ese workflow corre `pytest` en Python 3.9 y 3.12 en cada `push` y
`pull_request`; hacer clic en el badge lleva al historial de runs.
