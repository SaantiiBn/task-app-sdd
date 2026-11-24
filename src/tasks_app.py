import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

if __package__:
    from .models import Task
else:
    from models import Task


DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "tasks.json"


def valida_data_limit(valor: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
        raise argparse.ArgumentTypeError(
            "La data ha de tenir el format YYYY-MM-DD."
        )
    try:
        date.fromisoformat(valor)
    except ValueError as error:
        raise argparse.ArgumentTypeError("La data no és vàlida.") from error
    return valor


def normalitza_registre(registre: dict[str, Any]) -> dict[str, Any]:
    dades = dict(registre)
    if "titol" not in dades and "títol" in dades:
        dades["titol"] = dades["títol"]
    if "titol" not in dades and "title" in dades:
        dades["titol"] = dades["title"]
    if "assignatura" not in dades and "subject" in dades:
        dades["assignatura"] = dades["subject"]
    return dades


def carrega_tasques() -> list[Task]:
    if not DATA_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]\n", encoding="utf-8")
    contingut = DATA_FILE.read_text(encoding="utf-8").strip()
    if not contingut:
        return []
    registres = json.loads(contingut)
    return [Task.from_dict(normalitza_registre(registre)) for registre in registres]


def desa_tasques(tasques: list[Task]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    contingut = json.dumps(
        [tasca.to_dict() for tasca in tasques],
        ensure_ascii=False,
        indent=2,
    )
    DATA_FILE.write_text(contingut + "\n", encoding="utf-8")


def afegeix_tasca(
    titol: str, assignatura: str, data_limit: str | None = None
) -> Task:
    tasques = carrega_tasques()
    nova_tasca = Task(
        id=max((tasca.id for tasca in tasques), default=0) + 1,
        titol=titol,
        assignatura=assignatura,
        data_limit=data_limit,
    )
    tasques.append(nova_tasca)
    desa_tasques(tasques)
    return nova_tasca


def mostra_tasques(tasques: list[Task]) -> None:
    if not tasques:
        print("Registre de tasques buit.")
        return
    for tasca in tasques:
        print(
            f"[{tasca.id}] {tasca.titol} ({tasca.assignatura}) "
            f"- estat: {tasca.estat}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Eina CLI per gestionar tasques acadèmiques."
    )
    comandes = parser.add_subparsers(dest="comanda", required=True)

    afegir = comandes.add_parser("add", help="Afegeix una nova tasca pendent.")
    afegir.add_argument("--title", required=True, dest="titol")
    afegir.add_argument("--subject", required=True, dest="assignatura")
    afegir.add_argument(
        "--due",
        dest="data_limit",
        type=valida_data_limit,
        help="Data límit en format YYYY-MM-DD.",
    )

    comandes.add_parser("list", help="Mostra totes les tasques registrades.")

    args = parser.parse_args(argv)

    if args.comanda == "add":
        tasca = afegeix_tasca(args.titol, args.assignatura, args.data_limit)
        print(f"Tasca [ID: {tasca.id}] creada amb èxit")
    else:
        mostra_tasques(carrega_tasques())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
