\# TASKS.md - Tasks\_app



\## Increment 1: MVP - Creació i Llistat de Tasques

Objectiu: Tenir una versió CLI funcional per afegir i consultar tasques en JSON.



\### Tasques d'Execució:

\- \[x] Tasca 1.1: Crear estructura de directoris (`src/`, `test/`, `data/`) i fitxer `data/tasks.json` inicial. (Requisits RF-01 i RF-02) 

\- \[x] Tasca 1.2: Implementar model de dades `Task` a `src/models.py` amb mètodes de serialització JSON.

\- \[x] Tasca 1.3: Desenvolupar Tasks\_app a `src/tasks\_app.py` amb opcions `add` i `list`.(Requisits RF-03 i RF-04)

\- \[x] Tasca 1.4: Crear test d'integració a `test/test\_tasks\_app.py` segons els escenaris GS-01, GS-02 i GS-03.

\- \[x] Tasca 1.5: Validar execució amb OpenCode i verificar que tots els tests passen (`python3 -m pytest test`).


## Increment 2: Dates Límit, Edició i Alertes d'Urgència
Objectiu: Permetre gestionar dates límit (`--due`), editar tasques (`edit`), completar-les (`complete`) i mostrar avisos `[CADUCADA]` i `[URGENT]` al llistat.

### Tasques d'Execució:
- [x] Tasca 2.1: Actualitzar el model `Task` a `src/models.py` per incorporar l'atribut opcional `data_limit: str | None = None` mantenint retrocompatibilitat amb JSON antics. (Requisit RF-05)
- [x] Tasca 2.2: Actualitzar la comanda `add` a `src/tasks_app.py` per acceptar l'argument opcional `--due YYYY-MM-DD` validant el format de data. (Requisit RF-05)
- [x] Tasca 2.3: Implementar les subcomandes `edit --id <ID>` (per modificar `--title`, `--subject`, `--due`) i `complete --id <ID>` a `src/tasks_app.py` gestionant el cas d'ID inexistent. (Requisits RF-06 i RF-07)
- [x] Tasca 2.4: Actualitzar la funció de llistat (`list`) a `src/tasks_app.py` per mostrar la data límit (si en té) i afegir les etiquetes `[CADUCADA]` i `[URGENT]` en tasques pendents segons la data actual. (Requisits RF-08 i RF-09)
- [x] Tasca 2.5: Afegir els nous tests d'integració a `test/test_tasks_app.py` cobrint els escenaris GS-04, GS-05, GS-06 i GS-07, i verificar amb `python3 -m pytest test` que tots els tests (antics i nous) passen.

## Increment 3: Modes Avançats de Llistat i Cerca
Objectiu: Afegir opcions de resum estadístic (`--summary`), filtrat per assignatura (`--subject`) i cerca per paraula clau (`--keyword`) a la comanda `list`.

### Tasques d'Execució:
- [ ] Tasca 3.1: Implementar la funció de càlcul estadístic i l'opció `list --summary` a `src/tasks_app.py` comptabilitzant total, pendents, completades, caducades i urgents. (Requisit RF-10)
- [ ] Tasca 3.2: Afegir els arguments opcionals `--subject` i `--keyword` a la subcomanda `list` de `src/tasks_app.py` permetent filtrar sense distinció de majúscules/minúscules (i combinables entre si). (Requisits RF-11 i RF-12)
- [ ] Tasca 3.3: Afegir els tests d'integració a `test/test_tasks_app.py` per als escenaris GS-08, GS-09 i GS-10, verificar amb `python3 -m pytest test` que tots els tests passen i actualitzar `data/tasks.json` amb dades de mostra variades.