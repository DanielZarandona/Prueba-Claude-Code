from dataclasses import asdict, dataclass
from datetime import datetime

PRIORITIES = ("alta", "media", "baja")


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    # Fecha y hora de creación en formato ISO 8601 (se autocompleta en __post_init__ si no se indica)
    created_at: str = ""
    priority: str = "media"

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")
        if self.priority not in PRIORITIES:
            raise ValueError(
                f"Prioridad inválida: {self.priority!r} (opciones: {', '.join(PRIORITIES)})"
            )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)
