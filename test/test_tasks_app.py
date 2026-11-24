import json
import subprocess
import sys
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
