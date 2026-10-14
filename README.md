# Motor de historias interactivas — «La última transmisión»

Parcial práctico de Ingeniería de Software. Motor genérico que carga historias desde archivos JSON, valida su contenido, muestra solo las opciones compatibles con lo ocurrido, aplica sus consecuencias y permite reiniciar y deshacer la última elección.

## Integrantes

- [COMPLETAR: nombre completo del integrante 1]
- [COMPLETAR: nombre completo del integrante 2]

## Versiones requeridas

- Python **3.10 o superior** (probado con 3.10.11 en Windows 11).
- pytest **≥ 7** (probado con 9.1.1), solo para ejecutar las pruebas. El motor usa únicamente la biblioteca estándar.

## Instalación

```bash
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Windows (cmd):         .venv\Scripts\activate.bat
# Linux / macOS:         source .venv/bin/activate
pip install -r requirements.txt
```

Todos los comandos se ejecutan desde la carpeta raíz del proyecto.

## Ejecución

```bash
python -m motor historias/la_ultima_transmision.json   # historia oficial
python -m motor historias/el_faro.json                 # segunda historia, mismo motor
python -m motor                                        # menú con las historias de historias/
python -m motor --validar historias/el_faro.json       # solo validar → «Historia válida: …», código 0
python -m motor --validar historias/invalidas/destino_inexistente.json   # error E99 (CA03), código 2
python -m motor --ayuda
```

Durante la partida:

| Entrada | Acción |
|---|---|
| número o `id` de una opción | elegir esa opción (solo las mostradas están habilitadas) |
| `d` / `deshacer` | deshacer la última elección (un nivel; solo se ofrece cuando es posible) |
| `r` / `reiniciar` | volver al inicio con las variables iniciales (borra el historial de deshacer) |
| `e` / `estado` | ver los valores de las variables |
| `?` / `ayuda` | ver los comandos |
| `q` / `salir` | terminar (también Ctrl+D / Ctrl+Z+Enter o Ctrl+C) |

Si una historia es inválida, el programa lista **todos** los errores con código, ubicación y causa, no abre la partida y termina con código 2.

## Pruebas

```bash
python -m pytest -v                    # 148 pruebas: U1–U6, I1, bloqueo, CLI y RNF
python scripts/ejecutar_pruebas.py     # igual, y guarda evidencias/resultados_pruebas.txt con fecha y versiones
python scripts/verificar_rnf.py        # mide RNF-01..03 y guarda evidencias/rnf/resultado_rnf.txt
```

Los nombres de las pruebas incluyen el escenario de la guía: `test_U1_…` a `test_U6_…`, `test_I1_…`, `test_RNF01_…`.

## Formato de contenido

Se usa el contrato JSON de referencia de la guía **sin cambios**.

| Elemento | Campo | Tipo | Significado |
|---|---|---|---|
| Historia | `titulo` | texto | nombre visible |
| | `inicio` | texto | `id` de la escena donde empieza la partida |
| | `variables` | objeto `{nombre: true/false}` | estado inicial; solo booleanos |
| | `escenas` | lista (no vacía) | escenas de la historia |
| Escena | `id` | texto | identificador único en la historia |
| | `texto` | texto | contenido que se muestra |
| | `final` | `true`/`false` | si es un desenlace |
| | `opciones` | lista | vacía si `final` es `true`; al menos una si es `false` |
| Opción | `id` | texto | único dentro de la escena |
| | `texto` | texto | etiqueta visible |
| | `destino` | texto | `id` de una escena existente |
| | `condiciones` | objeto `{variable: true/false}` | todas deben cumplirse; `{}` = siempre habilitada |
| | `efectos` | objeto `{variable: true/false}` | asignaciones al elegir; `{}` = no cambia nada |

Todos los campos son obligatorios (también `condiciones` y `efectos`, aunque estén vacíos). Las variables usadas en `condiciones` y `efectos` deben estar declaradas en `variables`. `0`, `1` o `"true"` **no** son booleanos: escriba `true` o `false` sin comillas.

Ejemplo mínimo completo:

```json
{
  "titulo": "Mini",
  "inicio": "puerta",
  "variables": {"tiene_llave": false},
  "escenas": [
    {"id": "puerta", "texto": "Una puerta cerrada.", "final": false, "opciones": [
      {"id": "buscar", "texto": "Buscar la llave", "destino": "puerta",
       "condiciones": {"tiene_llave": false}, "efectos": {"tiene_llave": true}},
      {"id": "abrir", "texto": "Abrir", "destino": "salida",
       "condiciones": {"tiene_llave": true}, "efectos": {}}
    ]},
    {"id": "salida", "texto": "Estás fuera.", "final": true, "opciones": []}
  ]
}
```

Códigos de error del validador: `ARCHIVO_ILEGIBLE`, `ESTRUCTURA_INVALIDA`, `CAMPO_FALTANTE`, `INICIO_INEXISTENTE`, `ESCENA_DUPLICADA`, `OPCION_DUPLICADA`, `DESTINO_INEXISTENTE`, `VARIABLE_NO_DECLARADA`, `VALOR_NO_BOOLEANO`, `OPCIONES_INCOMPATIBLES_CON_FINAL`.

## Rutas para demostrar cada final

**La última transmisión** (`historias/la_ultima_transmision.json`):

| Final | Ruta | Variables al final |
|---|---|---|
| E4 Rescate | `revisar` → `investigar` → `activar_codigo` | conoce_origen = verdadero, confia_en_la_voz = verdadero |
| E5 El eco | `revisar` → `continuar` → `activar_sin_verificar` | conoce_origen = falso, confia_en_la_voz = verdadero |
| E6 Silencio | `revisar` → (`investigar` o `continuar`) → `cortar` | confia_en_la_voz = falso |

Condición visible: en E3 aparece `activar_codigo` solo si se investigó, y `activar_sin_verificar` solo si no.

**El faro de Isla Gris** (`historias/el_faro.json`):

| Final | Ruta |
|---|---|
| `faro_rescate` | `faro_buscar_llave` → `faro_abrir_candado` → `faro_encender_lampara` |
| `faro_costa_oscura` | `faro_ir_a_la_puerta` → `faro_esperar_tormenta` (sin llave no aparece `faro_abrir_candado`) |
| `faro_costa_oscura` | `faro_buscar_llave` → `faro_abrir_candado` → `faro_bajar_sin_encender` |

**Deshacer y reiniciar** (ejemplo de la solicitud de cambio): `revisar` → `investigar` (E3, conoce_origen verdadero) → `d` (vuelve a E2, falso) → `d` («No hay ninguna elección que deshacer.») → `continuar` (E3 muestra `activar_sin_verificar` y `cortar`). Desde E4, E5 o E6, `d` vuelve a E3 con los valores previos. `r` reinicia en cualquier momento.

## Versiones (etiquetas Git)

| Etiqueta | Contenido |
|---|---|
| `v1-inicial` | Versión sin retroceso, previa a la solicitud de cambio (`8f6c941`, 2026-10-15 05:52 +0700). |
| `v2-cambio` | Deshacer implementado y probado (`4340385`, 2026-10-15 05:56 +0700). |

`git log --all --decorate` o `evidencias/historial_git.txt` muestran el historial completo.

## Demostración en video

[COMPLETAR: `entrega/video.mp4` incluido en el ZIP, o enlace con acceso para el docente.]

## Documentación

- `docs/informe.md` / `docs/informe.pdf` — informe (≤ 8 páginas de cuerpo).
- `docs/anexo.md` / `docs/anexo.pdf` — diagramas, matriz y capturas del tablero (`python scripts/generar_anexo.py` lo regenera).
- `docs/requisitos.md`, `docs/modelos.md`, `docs/arquitectura.md`, `docs/analisis_impacto_cambio.md`, `docs/trazabilidad.md`, `docs/backlog.md`, `docs/solicitud_cambio.md`.

## Empaquetado de la entrega

```bash
python scripts/empaquetar.py --simular ApellidoNombre ApellidoNombre   # revisa sin crear el ZIP
python scripts/empaquetar.py ApellidoNombre ApellidoNombre             # crea Parcial_<A>_<B>.zip
```

## Limitaciones conocidas

- Solo interfaz de consola; no hay guardado entre ejecuciones (fuera de alcance).
- Deshacer tiene un único nivel y no hay rehacer (así lo define la solicitud de cambio).
- Solo condiciones de igualdad y efectos de asignación sobre booleanos; no hay expresiones.
- No se analiza si todos los finales son alcanzables ni si existen escenas inalcanzables; la validación es estructural. (Las pruebas sí exploran las dos historias entregadas.)
- Si el `id` de una opción coincide con un comando (`d`, `r`, `q`, `e`, `?` o sus nombres largos), escribirlo ejecuta el comando; esa opción se elige por su número.
- Los IDs distinguen mayúsculas y minúsculas; los comandos no.
- Si un objeto JSON repite una clave, el lector JSON de Python conserva el último valor sin avisar.
- No quedan pruebas fallando en la última ejecución registrada.
