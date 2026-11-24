import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "src" / "tasks_app.py"


def executa_cli(directori: Path, *arguments: str) -> str:
    resultat = subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=directori,
        capture_output=True,
        text=True,
    )
    assert resultat.returncode == 0, resultat.stderr
    return resultat.stdout


def escriu_registre(
    directori: Path, registres: list[dict[str, object]]
) -> Path:
    fitxer = directori / "data" / "tasks.json"
    fitxer.parent.mkdir(parents=True, exist_ok=True)
    fitxer.write_text(
        json.dumps(registres, ensure_ascii=False),
        encoding="utf-8",
    )
    return fitxer


def test_gs01_creacio_correcta_duna_tasca(tmp_path: Path) -> None:
    sortida = executa_cli(
        tmp_path, "add", "--title", "Pràctica 1", "--subject", "RS"
    )

    assert sortida.strip() == "Tasca [ID: 1] creada amb èxit"
    fitxer = tmp_path / "data" / "tasks.json"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 1",
            "assignatura": "RS",
            "estat": "pendent",
        }
    ]


def test_gs02_llistat_buit(tmp_path: Path) -> None:
    sortida = executa_cli(tmp_path, "list")

    assert sortida.strip() == "Registre de tasques buit."
    fitxer = tmp_path / "data" / "tasks.json"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == []


def test_gs03_llistat_amb_registres(tmp_path: Path) -> None:
    fitxer = tmp_path / "data" / "tasks.json"
    fitxer.parent.mkdir(parents=True, exist_ok=True)
    fitxer.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "titol": "Pràctica 1",
                    "assignatura": "RS",
                    "estat": "pendent",
                },
                {
                    "id": 2,
                    "titol": "Examen parcial",
                    "assignatura": "SO",
                    "estat": "pendent",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    sortida = executa_cli(tmp_path, "list")

    assert sortida.splitlines() == [
        "[1] Pràctica 1 (RS) - estat: pendent",
        "[2] Examen parcial (SO) - estat: pendent",
    ]


def test_gs04_creacio_amb_data_limit(tmp_path: Path) -> None:
    sortida = executa_cli(
        tmp_path,
        "add",
        "--title",
        "Entrega SDD",
        "--subject",
        "RS",
        "--due",
        "2026-12-01",
    )

    assert sortida.strip() == "Tasca [ID: 1] creada amb èxit"
    fitxer = tmp_path / "data" / "tasks.json"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Entrega SDD",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": "2026-12-01",
        }
    ]


def test_gs05_modificacio_duna_tasca(tmp_path: Path) -> None:
    fitxer = escriu_registre(
        tmp_path,
        [
            {
                "id": 1,
                "titol": "Pràctica 1",
                "assignatura": "RS",
                "estat": "pendent",
                "data_limit": "2026-11-30",
            }
        ],
    )

    sortida = executa_cli(
        tmp_path,
        "edit",
        "--id",
        "1",
        "--title",
        "Pràctica 1 Corregida",
        "--due",
        "2026-12-05",
    )

    assert sortida.strip() == "Tasca [ID: 1] actualitzada amb èxit"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 1 Corregida",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": "2026-12-05",
        }
    ]


def test_gs06_completar_tasca(tmp_path: Path) -> None:
    fitxer = escriu_registre(
        tmp_path,
        [
            {
                "id": 1,
                "titol": "Pràctica 1",
                "assignatura": "RS",
                "estat": "pendent",
            }
        ],
    )

    sortida = executa_cli(tmp_path, "complete", "--id", "1")

    assert sortida.strip() == "Tasca [ID: 1] marcada com a completada"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 1",
            "assignatura": "RS",
            "estat": "completada",
        }
    ]


def test_gs07_llistat_amb_etiquetes(tmp_path: Path) -> None:
    avui = date.today()
    data_caducada = (avui - timedelta(days=4)).isoformat()
    data_urgent = (avui + timedelta(days=4)).isoformat()
    data_futura = (avui + timedelta(days=21)).isoformat()

    escriu_registre(
        tmp_path,
        [
            {
                "id": 1,
                "titol": "Tasca antiga",
                "assignatura": "RS",
                "estat": "pendent",
                "data_limit": data_caducada,
            },
            {
                "id": 2,
                "titol": "Tasca propera",
                "assignatura": "SO",
                "estat": "pendent",
                "data_limit": data_urgent,
            },
            {
                "id": 3,
                "titol": "Tasca futura",
                "assignatura": "BD",
                "estat": "pendent",
                "data_limit": data_futura,
            },
        ],
    )

    sortida = executa_cli(tmp_path, "list")

    assert sortida.splitlines() == [
        (
            f"[1] Tasca antiga (RS) - estat: pendent "
            f"- límit: {data_caducada} [CADUCADA]"
        ),
        (
            f"[2] Tasca propera (SO) - estat: pendent "
            f"- límit: {data_urgent} [URGENT]"
        ),
        (
            f"[3] Tasca futura (BD) - estat: pendent "
            f"- límit: {data_futura}"
        ),
    ]
