import argparse
import json
import re
import sys
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


def afegeix_argument_data_limit(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--due",
        dest="data_limit",
        type=valida_data_limit,
        help="Data límit en format YYYY-MM-DD.",
    )


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


def cerca_tasca(tasques: list[Task], id_tasca: int) -> Task | None:
    for tasca in tasques:
        if tasca.id == id_tasca:
            return tasca
    return None


def actualitza_tasca(
    id_tasca: int,
    titol: str | None = None,
    assignatura: str | None = None,
    data_limit: str | None = None,
) -> Task | None:
    tasques = carrega_tasques()
    tasca = cerca_tasca(tasques, id_tasca)
    if tasca is None:
        return None
    if titol is not None:
        tasca.titol = titol
    if assignatura is not None:
        tasca.assignatura = assignatura
    if data_limit is not None:
        tasca.data_limit = data_limit
    desa_tasques(tasques)
    return tasca


def completa_tasca(id_tasca: int) -> Task | None:
    tasques = carrega_tasques()
    tasca = cerca_tasca(tasques, id_tasca)
    if tasca is None:
        return None
    tasca.estat = "completada"
    desa_tasques(tasques)
    return tasca


def mostra_error_id(id_tasca: int) -> None:
    print(f"Error: no existeix cap tasca amb ID {id_tasca}.", file=sys.stderr)


def tipus_alerta(tasca: Task, avui: date) -> str:
    if tasca.estat != "pendent" or tasca.data_limit is None:
        return ""
    try:
        data_limit = date.fromisoformat(tasca.data_limit)
    except ValueError:
        return ""
    dies_restants = (data_limit - avui).days
    if dies_restants < 0:
        return "CADUCADA"
    if dies_restants < 7:
        return "URGENT"
    return ""


def etiqueta_alerta(tasca: Task, avui: date) -> str:
    alerta = tipus_alerta(tasca, avui)
    return f" [{alerta}]" if alerta else ""


def calcula_estadistiques(tasques: list[Task], avui: date) -> dict[str, int]:
    estadistiques = {
        "total": len(tasques),
        "pendents": 0,
        "completades": 0,
        "caducades": 0,
        "urgents": 0,
    }
    for tasca in tasques:
        if tasca.estat == "completada":
            estadistiques["completades"] += 1
        elif tasca.estat == "pendent":
            estadistiques["pendents"] += 1
            alerta = tipus_alerta(tasca, avui)
            if alerta == "CADUCADA":
                estadistiques["caducades"] += 1
            elif alerta == "URGENT":
                estadistiques["urgents"] += 1
    return estadistiques


def mostra_resum(tasques: list[Task]) -> None:
    estadistiques = calcula_estadistiques(tasques, date.today())
    print(
        "Resum de tasques - "
        f"Total: {estadistiques['total']} | "
        f"Pendents: {estadistiques['pendents']} | "
        f"Completades: {estadistiques['completades']} | "
        f"Caducades: {estadistiques['caducades']} | "
        f"Urgents: {estadistiques['urgents']}"
    )


def filtra_tasques(
    tasques: list[Task],
    assignatura: str | None = None,
    paraula_clau: str | None = None,
) -> list[Task]:
    filtrades = tasques
    if assignatura is not None:
        valor = assignatura.casefold()
        filtrades = [
            tasca
            for tasca in filtrades
            if tasca.assignatura.casefold() == valor
        ]
    if paraula_clau is not None:
        valor = paraula_clau.casefold()
        filtrades = [
            tasca for tasca in filtrades if valor in tasca.titol.casefold()
        ]
    return filtrades


def mostra_tasques(tasques: list[Task]) -> None:
    if not tasques:
        print("Registre de tasques buit.")
        return
    avui = date.today()
    for tasca in tasques:
        linia = (
            f"[{tasca.id}] {tasca.titol} ({tasca.assignatura}) "
            f"- estat: {tasca.estat}"
        )
        if tasca.data_limit is not None:
            linia += f" - límit: {tasca.data_limit}"
            linia += etiqueta_alerta(tasca, avui)
        print(linia)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Eina CLI per gestionar tasques acadèmiques."
    )
    comandes = parser.add_subparsers(dest="comanda", required=True)

    afegir = comandes.add_parser("add", help="Afegeix una nova tasca pendent.")
    afegir.add_argument("--title", required=True, dest="titol")
    afegir.add_argument("--subject", required=True, dest="assignatura")
    afegeix_argument_data_limit(afegir)

    llistar = comandes.add_parser(
        "list", help="Mostra totes les tasques registrades."
    )
    llistar.add_argument(
        "--summary",
        dest="resum",
        action="store_true",
        help="Mostra un resum estadístic de les tasques.",
    )
    llistar.add_argument(
        "--subject",
        dest="assignatura_filtre",
        help="Filtra les tasques per assignatura.",
    )
    llistar.add_argument(
        "--keyword",
        dest="paraula_clau",
        help="Filtra les tasques per paraula clau al títol.",
    )

    editar = comandes.add_parser("edit", help="Modifica una tasca existent.")
    editar.add_argument("--id", required=True, type=int)
    editar.add_argument("--title", dest="titol")
    editar.add_argument("--subject", dest="assignatura")
    afegeix_argument_data_limit(editar)

    completar = comandes.add_parser(
        "complete", help="Marca una tasca com a completada."
    )
    completar.add_argument("--id", required=True, type=int)

    args = parser.parse_args(argv)

    if args.comanda == "add":
        tasca = afegeix_tasca(args.titol, args.assignatura, args.data_limit)
        print(f"Tasca [ID: {tasca.id}] creada amb èxit")
    elif args.comanda == "edit":
        if all(
            valor is None
            for valor in (args.titol, args.assignatura, args.data_limit)
        ):
            print(
                "Error: cal especificar almenys un atribut per modificar.",
                file=sys.stderr,
            )
            return 1
        tasca = actualitza_tasca(
            args.id, args.titol, args.assignatura, args.data_limit
        )
        if tasca is None:
            mostra_error_id(args.id)
            return 1
        print(f"Tasca [ID: {tasca.id}] actualitzada amb èxit")
    elif args.comanda == "complete":
        tasca = completa_tasca(args.id)
        if tasca is None:
            mostra_error_id(args.id)
            return 1
        print(f"Tasca [ID: {tasca.id}] marcada com a completada")
    else:
        tasques = filtra_tasques(
            carrega_tasques(), args.assignatura_filtre, args.paraula_clau
        )
        if args.resum:
            mostra_resum(tasques)
        else:
            mostra_tasques(tasques)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
