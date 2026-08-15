# task-tracker

CLI simple para gestionar tareas (agregar, listar, completar, eliminar),
guardadas en un archivo JSON local en `./data/tasks.json`.

## Estructura del proyecto

```
task-tracker/
├── src/
│   └── task_tracker/
│       ├── __init__.py
│       ├── __main__.py   # permite `python -m task_tracker`
│       ├── cli.py         # parseo de argumentos y comandos
│       ├── models.py      # modelo Task
│       └── storage.py     # persistencia en JSON
├── tests/
│   ├── test_cli.py
│   └── test_storage.py
├── data/
│   └── tasks.json          # se crea automáticamente al agregar la primera tarea
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
```

Por defecto las tareas se guardan en `./data/tasks.json` (relativo al
directorio desde el que se ejecuta el comando). Puede usarse otra ruta con
`--data`:

```bash
task-tracker --data otra_ruta/tasks.json list
```

## Tests

```bash
pip install -r requirements.txt
pytest
```
