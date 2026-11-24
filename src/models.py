import json
from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    id: int
    titol: str
    assignatura: str
    estat: str = "pendent"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "titol": self.titol,
            "assignatura": self.assignatura,
            "estat": self.estat,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, dades: dict[str, Any]) -> "Task":
        return cls(
            id=int(dades["id"]),
            titol=str(dades["titol"]),
            assignatura=str(dades["assignatura"]),
            estat=str(dades.get("estat", "pendent")),
        )

    @classmethod
    def from_json(cls, text: str) -> "Task":
        return cls.from_dict(json.loads(text))
