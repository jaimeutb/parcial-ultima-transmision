# Prompt Claude Code — Parcial «La última transmisión»

## Cara pakai (baca dulu, jangan ikut ditempel)

1. Buka terminal di folder repo kalian (atau folder kosong kalau belum ada kode sama sekali).
2. Buat folder `enunciado/` dan taruh di dalamnya: PDF panduan, PDF *Solicitud de cambio* (unduh dari Savio), dan `la_ultima_transmision.json`.
3. Isi blok **DATOS DEL EQUIPO** di bawah.
4. Simpan file ini di root repo sebagai `PROMPT_CLAUDE_CODE.md`, jalankan `claude`, lalu ketik:
   `Lee PROMPT_CLAUDE_CODE.md (desde "INICIO DEL PROMPT") y ejecútalo completo.`
5. **Cek jam tutup di Savio.** Urutan fase sudah diatur berdasarkan bobot nilai: kode + tes dulu, dokumen kemudian. Kalau waktu mepet, minta Claude Code berhenti setelah Fase 3 dan lanjutkan dokumen secara manual.
6. Yang **harus kalian kerjakan sendiri** setelahnya: isi semua `[COMPLETAR]`, screenshot tablero awal & akhir, baca ulang laporan, rekam video MP4 ≤ 6 menit, ekspor PDF, jalankan skrip ZIP, upload, simpan bukti upload.
7. Partner juga harus punya commit sendiri (misalnya dokumen atau tes), karena aporte per integrante dicek dari riwayat Git.
8. Pemakaian Claude Code **wajib dideklarasikan** di bagian "Fuentes y herramientas" laporan (panduan bagian 6). Prompt ini sudah menyiapkan bagian itu.

---

## DATOS DEL EQUIPO (isi sebelum menjalankan)

```
Integrante 1 (nombre completo): [ ]      Para el ZIP (ApellidoNombre, sin tildes): [ ]
Integrante 2 (nombre completo): [ ]      Para el ZIP (ApellidoNombre, sin tildes): [ ]
Hora de apertura del parcial: [ ]        Hora de cierre: [ ]
Lenguaje: Python 3.10+ (si el repo ya usa otro lenguaje, mantener ese)
```

---

## === INICIO DEL PROMPT ===

You are helping a pair of students finish a 12-hour Software Engineering practical exam. They are allowed to use AI tools as long as they declare them, so everything you produce must be verifiable and honest.

### Sources of truth
- If `enunciado/` contains the guide PDF and the change-request PDF, read them first. This prompt summarizes them; if anything conflicts, the PDFs win.
- The official story file is `enunciado/la_ultima_transmision.json` (official option ID in E3 is `activar_codigo`). Copy it unchanged to `historias/la_ultima_transmision.json`.

### Language
- Code identifiers in Spanish, matching the guide's vocabulary (`Historia`, `Escena`, `Opcion`, `Sesion`, `condiciones`, `efectos`, `destino`).
- All user-facing text, error messages, documentation and commit messages in Spanish.

### Hard rules
1. Never rewrite git history, never force-push, never delete tags, never fake dates (no `GIT_*_DATE`, no `--date`).
2. The engine (`motor/`) must not contain any scene ID, option ID or variable name from a specific story. A test enforces this.
3. No traceback may ever reach the user. The CLI catches errors and prints controlled Spanish messages.
4. Commit after each phase (and after meaningful sub-steps) with small messages that reference RF or test IDs, e.g. `RF09: deshacer restaura escena y variables (U6)`.
5. Never invent facts about the team: names, who did what, questions actually sent to the teacher and answers received, peer-review findings, learnings, board state. Write `[COMPLETAR: …]` with a suggestion instead.
6. If code already exists, extend and fix it. Do not rewrite from scratch unless it is unusable, and ask me first in that case. If it is in another language, keep that language and map the structure below to it.
7. Never weaken or delete an assertion to make a test pass. Fix the code. Record any failure you cannot fix in README → "Limitaciones conocidas".
8. Use a task list and work through the phases autonomously. The only planned stop is the tag question in Phase 0.

---

### Phase 0 — Inspect and protect the starting version
1. Run `git status`, `git tag`, and `git log --date=iso --pretty=format:"%h | %an | %ad | %d %s" -n 30`.
2. If there is no repo, run `git init`.
3. If there is uncommitted work, commit it as `WIP: versión disponible al recibir la solicitud de cambio`.
4. If tag `v1-inicial` does not exist:
   - If there are commits, show me the commit list with dates and ask which one was the version we had when the change request was published (hour 6). Tag that commit `v1-inicial`.
   - If there is no code at all, tell me. Then do Phase 1 (without undo), commit, tag `v1-inicial`, and record the real date/time of that tag in `docs/analisis_impacto_cambio.md`. Do not pretend it was created earlier.
5. Create `docs/solicitud_cambio.md` with the transcription at the end of this prompt.
6. Copy the official story to `historias/la_ultima_transmision.json`.

### Phase 1 — Base version (needs N01–N06)
Skip whatever already exists and works; fill the gaps.

**Structure (Python 3.10+, standard library `json`, only `pytest` as a dependency):**
```
motor/__init__.py
motor/modelo.py       Historia, Escena, Opcion (immutable dataclasses)
motor/cargador.py     read file → dict; controlled errors for missing/unreadable/invalid JSON
motor/validador.py    validate dict → list of ErrorContenido; build the model only if there are 0 errors
motor/sesion.py       game rules; no input/print
motor/cli.py          console interface; the only module with input/print
motor/__main__.py     python -m motor [ruta]   |   python -m motor --validar ruta
historias/la_ultima_transmision.json
historias/el_faro.json                          second story (see below)
historias/invalidas/destino_inexistente.json    copy of the official story with destino "E99" (CA03 + demo)
tests/
pytest.ini            [pytest] pythonpath = .  testpaths = tests
requirements.txt      pytest>=7
```

**Content contract (keep it exactly; document it in the README):**
- Historia: `titulo` (text), `inicio` (scene ID), `variables` (map of initial booleans), `escenas` (list).
- Escena: `id` (unique), `texto`, `final` (bool), `opciones` (list, empty if final).
- Opcion: `id` (unique within the scene), `texto`, `destino` (existing scene ID), `condiciones` (map of equalities), `efectos` (map of assignments).
- An empty `condiciones` map enables the option. All conditions must hold. An empty `efectos` map leaves variables unchanged.

**Validation.** Collect ALL errors and reject the file before any session starts. Each `ErrorContenido` has a stable `codigo` (for tests), a Spanish `mensaje` stating the cause, and a `ubicacion` (path such as `escenas[2].opciones[0].destino` plus the scene/option ID when known). Codes:

| Código | Category in the guide |
|---|---|
| `ARCHIVO_ILEGIBLE` | File missing, unreadable, or not valid JSON |
| `ESTRUCTURA_INVALIDA` | Root is not an object, or a field has the wrong type (e.g. `escenas` not a list, `condiciones` not an object, `id`/`texto` not a string, `final` not a bool, empty `escenas`) |
| `CAMPO_FALTANTE` | A required field is missing at story, scene or option level |
| `INICIO_INEXISTENTE` | `inicio` does not match any scene |
| `ESCENA_DUPLICADA` | Repeated scene ID |
| `OPCION_DUPLICADA` | Repeated option ID within the same scene |
| `DESTINO_INEXISTENTE` | `destino` does not match any scene |
| `VARIABLE_NO_DECLARADA` | `condiciones` or `efectos` use a variable not declared in `variables` |
| `VALOR_NO_BOOLEANO` | Non-boolean value in `variables`, `condiciones` or `efectos` (reject `0`, `1`, `"true"`; use `isinstance(v, bool)`) |
| `OPCIONES_INCOMPATIBLES_CON_FINAL` | A final scene with options, or a non-final scene with zero options |

**Runtime block.** If a non-final scene has zero enabled options, the session reports `esta_bloqueada = True`. The CLI says so ("No hay opciones disponibles en esta escena") and offers to restart.

**Session API (`motor/sesion.py`), suggested shape:**
```python
class Sesion:
    def __init__(self, historia: Historia): ...
    escena_actual: Escena                     # property
    variables: dict[str, bool]                # property returning a COPY
    def opciones_habilitadas(self) -> list[Opcion]
    def elegir(self, id_opcion: str) -> ResultadoAccion
        # codes: OK | OPCION_INEXISTENTE | OPCION_NO_HABILITADA | PARTIDA_FINALIZADA
    def reiniciar(self) -> None
    es_final: bool                            # property
    esta_bloqueada: bool                      # property
```
- `elegir` checks the ID against the current scene's options **and** their conditions under the current variables. CA02: sending `activar_codigo` directly while `conoce_origen` is false must be rejected.
- Apply effects to a copy, then commit scene + variables together. A rejected input changes nothing at all.
- The session never mutates the `Historia` model or the initial variables (always copy).

**CLI.**
- Show the title, the scene text and the enabled options numbered. Accept a number or an option ID.
- Commands: `r`/`reiniciar`, `q`/`salir`, `?`/`ayuda`. On a final scene, show «FIN» and offer restart/quit.
- Handle EOF and Ctrl+C gracefully.
- For an invalid story, print every error and exit with code 2 without starting.
- `--validar` prints «Historia válida» or the list of errors.

**Second story `historias/el_faro.json`.** Original, in Spanish, 4–5 scenes. Use distinctive IDs of its own (e.g. `faro_muelle`): not E-prefixed and not equal to contract field names. Use its own variable names, at least one condition, at least one effect, and at least two finals. It must be playable to every final with zero changes to `motor/`.

Commit and run the tests that exist so far.

### Phase 2 — Change request: undo (see transcription at the end)
Implementation guidance (the guide does not require a specific pattern; this one is the simplest that satisfies every rule):
- Keep a single snapshot `_anterior: tuple[str, dict[str, bool]] | None` = (scene ID, **copy** of the variables). Save it immediately before applying a choice that has passed all validation.
- `deshacer() -> ResultadoAccion` (`OK` | `SIN_RETROCESO`): if `_anterior` is `None`, change nothing; otherwise restore the scene and a copy of the variables, then set `_anterior = None`.
- `puede_deshacer: bool` property.
- `reiniciar()` restores the initial state **and** clears `_anterior`.
- An invalid choice (nonexistent, not enabled, or on a final) leaves both the state and `_anterior` untouched.
- Undo works from finals (E4/E5/E6 → E3 with the previous values) and from a blocked scene. No redo.
- CLI: add `d`/`deshacer`, and show it only when `puede_deshacer` is true.
- Add a new requirement with the next free RF ID and acceptance criteria covering the 5 rules. State that it replaces the provisional «sin retroceso» agreement, which resolves the writer-vs-designer conflict.

### Phase 3 — Automated tests (pytest)
Name tests so the scenario ID shows in the output (`test_U1_…`, `test_I1_…`). Each test has a docstring stating its inputs and expected result, and real assertions. Use a helper that loads a deep copy of the official story to build variants in memory.

- **U1 Condiciones.** Parametrize `conoce_origen` true/false → E3 shows exactly `{activar_codigo, cortar}` / `{activar_sin_verificar, cortar}`. Also a tiny in-memory story whose option has two conditions (all must hold). Covers CA01.
- **U2 Elección válida.** `investigar` → E3 with `conoce_origen` true. An option with empty `efectos` keeps the variables.
- **U3 Entrada inválida.** A nonexistent ID and a not-enabled ID (`activar_codigo` with `conoce_origen` false, CA02) leave scene and variables identical and return the right code. Choosing on a final → `PARTIDA_FINALIZADA`.
- **U4 Validación.** Parametrized: one case per error code (including destino `E99` = CA03). Assert the code **and** that the message/location contains the offending ID or field. Assert no session is created. Use real files in `tmp_path` for unreadable / invalid JSON.
- **Bloqueo.** An in-memory story whose non-final scene has every option disabled → `esta_bloqueada`; `reiniciar` works and `deshacer` returns to the previous scene.
- **U5 Reiniciar.** Restores `inicio` and the initial variables. *Extended:* afterwards `puede_deshacer` is false and `deshacer` returns `SIN_RETROCESO`.
- **U6 Deshacer (new).**
  - Teacher's example, exactly: at E2 choose `investigar` → E3 with `conoce_origen` true; `deshacer` → E2 with `conoce_origen` false; second `deshacer` → `SIN_RETROCESO` and nothing changes; `continuar` → E3 shows exactly `activar_sin_verificar` and `cortar`.
  - Variants: no undo at the start; an invalid input after a valid choice preserves the history (undo still restores); a new valid choice re-enables undo; ALL variables are restored (check `confia_en_la_voz` too); the snapshot is a copy, not a reference.
- **I1 Integración.** Load the real file from disk and play the three routes to E4, E5 and E6, asserting the final scene and variables. *Extended:* from each final, `deshacer` → E3 with the previous values (e.g. E4 → E3 with `conoce_origen` true and `confia_en_la_voz` false). Also load `el_faro.json` and reach a final.

### Phase 3b — Non-functional requirements (tests in `tests/test_rnf.py`, plus `scripts/verificar_rnf.py` writing `evidencias/rnf/resultado_rnf.txt`)
- **RNF-01 Modificabilidad del contenido.** A new story (≥ 3 scenes, ≥ 1 condition, ≥ 1 effect) runs with 0 lines changed in `motor/`.
  Verification: (a) a test plays `el_faro.json` to every final; (b) a test reads both story files, collects every scene ID and option ID, and asserts none appears as a standalone string literal (`"E3"` / `'E3'`) in `motor/*.py`, and no variable name appears as a whole word.
- **RNF-02 Claridad de errores.** 100 % of the 10 error codes produce a Spanish message with the cause and the ID/field involved, and 0 tracebacks.
  Verification: the U4 parametrization plus a subprocess test (`sys.executable -m motor --validar <file>`) per invalid fixture, asserting exit code 2, that the ID appears in the output, and that `"Traceback"` does not.
- **RNF-03 Confiabilidad.** Over 1 000 seeded random sequences of 50 actions (valid IDs, invalid IDs, random strings, `deshacer`, `reiniciar`): 0 unhandled exceptions, and invariants hold after every action (current scene exists, variable keys equal the declared ones, all values are bool, a final has no enabled options).
  Verification: report the counts in the results file.

Run `python -m pytest -v` and save the output to `evidencias/resultados_pruebas.txt`, preceded by a header with the date, Python version and pytest version. When everything passes: commit, tag `v2-cambio`.

### Phase 4 — Documentation (Spanish, in `docs/`)
Write drafts with `[COMPLETAR]` where only the students can answer. Names in the diagrams must match the final code.

- **`docs/requisitos.md`**
  - Atomic RFs: ID, observable behavior, linked N0x, acceptance criterion (Dado / Cuando / Entonces). Cover N01–N06, every validation category, the runtime block, restart, and the change RF.
  - Three RNFs, each with metric, procedure and evidence path.
  - Three questions with answers or assumptions, e.g.: retroceso → provisional agreement, later resolved by the change; formato → JSON; escena sin opciones habilitadas → inform and allow restart.
  - The writer-vs-designer conflict and how it was resolved.
  - «Defecto detectado en revisión cruzada»: `[COMPLETAR]` plus a suggested candidate for the students to confirm or replace.
- **`docs/modelos.md`** (Mermaid, small):
  - Contexto.
  - Casos de uso: actors Lector and Escritor; Cargar/Validar historia, Leer escena, Elegir opción, Deshacer, Reiniciar.
  - Clases del dominio.
  - Secuencia «elegir una opción», including the snapshot.
  - Estados de una sesión: EnCurso, Bloqueada, Finalizada, plus the rejected load; transitions elegir/deshacer/reiniciar with guards.
- **`docs/arquitectura.md`**
  - Component/layer diagram (Contenido JSON → Cargador → Validador → Modelo → Sesión ← CLI) with responsibilities and relations.
  - Two decisions (context, alternatives, choice, consequences):
    1. Validate everything before playing vs. validate lazily during the game.
    2. Undo with a single snapshot vs. a history stack / Command pattern / replaying choices from the start.
  - The separation of content, rules and interface, shown by the second story.
  - One detailed-design decision: `Sesion` has no I/O, so it is testable and the CLI is only an adapter.
  - Libraries and licenses: Python (PSF License), pytest (MIT).
- **`docs/analisis_impacto_cambio.md`**
  - Starting version: tag, hash, real date.
  - Affected requirements, models (classes, sequence, states), components (`sesion.py`, `cli.py`), tests (U6 new; U5 and I1 extended), backlog items, traceability rows, risks.
  - The evidence that it works: test names, tag `v2-cambio`.
- **`docs/trazabilidad.md`.** Matrix: every RF (including the change) and RNF → N0x → model(s) → file/function → test (`archivo::test`) → evidence path. Every cell must be a locatable name or path.
- **`docs/backlog.md`.** Items with priority, owner `[COMPLETAR]` and status; mark the items added at hour 6. Include a Definition of Done.
- **`docs/informe.md`.** Draft report, ≤ 8 pages of body, following the rubric order:
  1. Identification `[COMPLETAR]`.
  2. Problem, actors, scope; two risks with mitigation; quality-attribute prioritization; a professional-responsibility decision.
  3. Process vs. one alternative; specification/development/validation/evolution; two agile practices used and one discarded; DoD; learning + improvement action `[COMPLETAR]`.
  4. Summary of RF/RNF, questions, defect.
  5. Models (reference the annex).
  6. Architecture.
  7. Implementation and tests, with real numbers.
  8. Change and impact.
  9. Contributions per member linked to commits `[COMPLETAR]`.
  10. Sources and tools: Python, pytest, licenses, and Claude Code, stating what it was used for and how the students verified the results `[COMPLETAR with the truthful details]`.
- **`docs/anexo.md`.** Diagrams, traceability matrix, board-screenshot placeholders.
- **PDF and diagram rendering.** If `pandoc` with a PDF engine is already available, generate `docs/informe.pdf` and `docs/anexo.pdf`; do not install heavy tools — otherwise tell me to export from Word/Google Docs. If `npx @mermaid-js/mermaid-cli` works, render the diagrams to `docs/diagramas/*.png`; otherwise keep the Mermaid sources and tell me to use mermaid.live.
- **`README.md`.** Members `[COMPLETAR]`, required versions, installation (venv + `pip install -r requirements.txt`), how to run each story and `--validar`, how to run the tests, the content format (contract table + small example), and the routes to each final:
  - E4: revisar → investigar → activar_codigo
  - E5: revisar → continuar → activar_sin_verificar
  - E6: revisar → (investigar o continuar) → cortar

  Also include the routes for the second story, how to undo/restart, the tags `v1-inicial` / `v2-cambio`, the video link `[COMPLETAR]`, and known limitations.

### Phase 5 — Evidence and packaging
- `evidencias/tablero/LEEME.md` listing the required screenshots (initial and final board).
- `scripts/empaquetar.py ApellidoNombre ApellidoNombre`:
  - Validates the names (no spaces, no accents) and builds `Parcial_<A>_<B>.zip`.
  - Includes code, stories, tests, docs (with the PDFs), evidencias, README and `entrega/video.mp4` if present.
  - Excludes `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `*.pyc`, `enunciado/`.
  - Re-opens the ZIP to check that it extracts, lists the contents, and warns about missing items: informe.pdf, anexo.pdf, video or README link, board screenshots, historial_git.txt, resultados_pruebas.txt.
  - Do a dry run only; do not build the final ZIP until I say the placeholders are filled.
- As the very last step, after the final commit: `git log --all --decorate --date=iso --pretty=format:"%h | %an <%ae> | %ad | %d %s" > evidencias/historial_git.txt`.

### Final report to me
Short summary of what was done; number of tests and how many pass; tags created; the full list of remaining `[COMPLETAR]` items (grep them); and the checklist from section 8 of the guide, each item marked ✅ / ⚠️ / ❌.

---

### Transcription — Solicitud de cambio del parcial (save as `docs/solicitud_cambio.md`)

> **Solicitud de cambio del parcial — La última transmisión**
> Material para entregar al cumplirse la hora 6. El cierre del parcial se mantiene en la hora 12.
>
> **Nueva decisión del cliente**
> El colectivo ha acordado que el lector debe poder deshacer su última decisión. Al hacerlo, también deben revertirse todas sus consecuencias. Esta solicitud reemplaza el acuerdo provisional de no implementar retroceso.
>
> | Regla | Comportamiento obligatorio |
> |---|---|
> | Restauración | Deshacer restaura exactamente la escena y todas las variables anteriores a la última elección válida. |
> | Un solo nivel | Después de deshacer, no se permite otro retroceso hasta realizar una nueva elección válida. No se exige rehacer. |
> | Inicio y reinicio | Al comenzar no hay retroceso disponible. Reiniciar elimina el historial y restaura el estado inicial. |
> | Entrada inválida | Una opción inexistente o no habilitada no modifica la sesión ni sustituye el historial de la última elección válida. |
> | Desde un final | Es posible deshacer desde E4, E5 o E6; se regresa a E3 y se restauran los valores previos a esa elección. |
>
> **Trabajo y evidencia**
> Conserven la versión disponible al recibir la solicitud, aunque esté incompleta. Redacten el nuevo requisito con su propio identificador y aceptación; analicen el impacto; actualicen backlog, modelos, código, pruebas y trazabilidad. No se exige una arquitectura o patrón específico para resolverlo.
>
> **Ampliación de pruebas**
> Añadan U6: deshacer restaura escena y variables y consume la posibilidad de retroceder. Usen variantes para comprobar que una entrada inválida preserva el historial y que una nueva elección vuelve a habilitar un retroceso. Extiendan U5 para verificar que reiniciar elimina el historial, e I1 para deshacer desde un final después de cargar el archivo y recorrer la historia.
>
> Ejemplo: desde E2, investigar lleva a E3 con conoce_origen verdadero. Deshacer devuelve a E2 con conoce_origen falso. Un segundo intento de deshacer no cambia nada. Al continuar sin investigar, E3 muestra activar sin verificar y cortar comunicación.
>
> Incluyan el resultado en el informe y la demostración ya solicitados. Este anexo no agrega páginas obligatorias ni un video adicional. Su evaluación corresponde a los 4 puntos de comportamiento nuevo y pruebas dentro del criterio de cambio; análisis y trazabilidad conservan sus pesos publicados.

## === FIN DEL PROMPT ===
