# Análisis de impacto — Solicitud de cambio «deshacer la última decisión»

Solicitud transcrita en [solicitud_cambio.md](solicitud_cambio.md).

## 1. Versión de partida

| Dato | Valor |
|---|---|
| Etiqueta | `v1-inicial` (anotada) |
| Commit | `10dfc3a` (`10dfc3a14f66f8238589d02c8f935fc5369770a1`) |
| Fecha real del commit y de la etiqueta | 2026-10-15 05:52:29 +0700 |
| Contenido | Motor completo sin retroceso: carga, validación (10 códigos), sesión, CLI, segunda historia, pruebas U1–U5, I1, bloqueo y CLI (95 pruebas, todas pasan en ese commit). |

**Declaración honesta sobre esta etiqueta.** El repositorio se creó con `git init` en esta misma sesión de trabajo; antes no había código. La versión inicial se construyó con ayuda de Claude Code siguiendo el alcance inicial (sin retroceso) y se etiquetó `v1-inicial` en la fecha real indicada arriba, **sin modificar fechas**. El texto de la solicitud de cambio ya estaba disponible en el prompt usado, pero no se incorporó nada de ella antes de la etiqueta: `docs/solicitud_cambio.md` y todo el código de deshacer se agregaron en commits posteriores (`7cc7050` en adelante).
**Cambio de identidad en el historial.** Los commits se crearon originalmente con la identidad Git global del equipo usado (`workaumz-debug`). Antes del primer `push`, el autor y el committer de los 17 commits se reescribieron a `jaimeutb <eudonemia@gmail.com>` con `git filter-branch --env-filter`, **conservando las fechas, los mensajes y el contenido** (mismo árbol de archivos). Por eso cambiaron los hashes; los que aparecen en este documento son los nuevos. Las etiquetas se recrearon apuntando a los commits reescritos con su fecha original.

[COMPLETAR: si al recibir la solicitud a la hora 6 tenían otra versión (en otro repositorio, carpeta o máquina), indicarlo aquí con su fecha real; si no, confirmar que `v1-inicial` es la versión de partida y a qué hora del parcial (hora de apertura + N) se creó.]

## 2. Versión resultante

| Dato | Valor |
|---|---|
| Etiqueta | `v2-cambio` (anotada) |
| Commit | `bef51ab` (`bef51ab724212ebc64c1f2e3bf5a1c4fd66421fe`) |
| Fecha real | 2026-10-15 05:56:42 +0700 |
| Commits del cambio | `7cc7050` solicitud · `8a8b6bb` RF17 sesión · `af81416` RF17 CLI · `78afafc` pruebas U6/U5/I1 · `bc96563` RNF · `bef51ab` evidencias |

`git diff --stat v1-inicial v2-cambio -- motor/`: `motor/sesion.py` +23/−1, `motor/cli.py` +9/−1. Sin cambios en `modelo.py`, `validador.py`, `cargador.py` ni en las historias.

## 3. Elementos afectados

### Requisitos
| Elemento | Impacto |
|---|---|
| Acuerdo provisional «sin retroceso» (P1, §5 de requisitos) | **Reemplazado** por la decisión del cliente. |
| RF17 (nuevo) | Deshacer un nivel, con criterios RF17.1–RF17.5 (una por regla de la solicitud). |
| RF09 Reiniciar | Ampliado: reiniciar también elimina el historial de retroceso. |
| RF06 Rechazo de entradas | Ampliado: una entrada rechazada tampoco sustituye el historial. |
| RF08 Final, RF16 Bloqueo | Ampliados: desde un final o una escena bloqueada se puede deshacer. |
| RF01–RF05, RF07, RF10–RF15, RNF-01, RNF-02 | Sin cambios. |
| RNF-03 | Ampliado: las secuencias aleatorias incluyen la acción `deshacer` e invariantes de «acción rechazada no cambia el estado». |

### Modelos ([modelos.md](modelos.md))
| Modelo | Impacto |
|---|---|
| Casos de uso | Nuevo caso «Deshacer última elección». |
| Clases | `Sesion` gana `_anterior`, `puede_deshacer` y `deshacer()`; nuevo código `SIN_RETROCESO` en `ResultadoAccion`. |
| Secuencia «elegir» | Nuevo paso: guardar la instantánea después de validar y antes de confirmar. |
| Estados | Nuevas transiciones `deshacer [puede_deshacer]` desde EnCurso, Finalizada y Bloqueada hacia EnCurso. |
| Contexto | Sin cambios de actores; el lector dispone de una acción más. |

### Componentes
| Archivo | Cambio |
|---|---|
| `motor/sesion.py` | Instantánea única, `deshacer()`, `puede_deshacer`, `reiniciar()` limpia el historial. |
| `motor/cli.py` | Comando `d`/`deshacer`, visible solo cuando `puede_deshacer`; «FIN» y bloqueo lo ofrecen. |
| `motor/modelo.py`, `validador.py`, `cargador.py`, `historias/*.json` | Sin cambios (el formato de contenido no cambia). |

### Pruebas
| Prueba | Tipo |
|---|---|
| `tests/test_deshacer.py` (U6): ejemplo del docente, inicio sin retroceso, entrada inválida preserva historial, elegir en un final no lo borra, nueva elección lo rehabilita, solo un nivel, todas las variables, instantánea como copia, desde E4/E5/E6 | **Nueva** |
| `tests/test_sesion.py::test_U5_extendido_reiniciar_elimina_el_historial_de_deshacer` | **Extendida** (U5) |
| `tests/test_integracion.py::test_I1_extendido_deshacer_desde_cada_final_tras_cargar_el_archivo`, `test_I1_segunda_historia_deshacer_desde_un_final` | **Extendida** (I1) |
| `tests/test_sesion.py::test_bloqueo_deshacer_vuelve_a_la_escena_anterior` | Extendida (bloqueo) |
| `tests/test_cli.py::test_cli_deshacer_solo_se_ofrece_cuando_hay_retroceso`, `test_cli_deshacer_desde_FIN` | Nuevas (interfaz) |
| `tests/test_rnf.py::test_RNF03_*` | Ampliada con `deshacer` |

### Backlog y trazabilidad
- Backlog: ítems B13–B17 marcados «agregado hora 6» en [backlog.md](backlog.md).
- Trazabilidad: nueva fila RF17 y filas RF06, RF08, RF09, RF16, RNF-03 actualizadas en [trazabilidad.md](trazabilidad.md).

## 4. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| La instantánea comparte referencia con el estado actual y un efecto posterior la altera. | Se guarda y se restaura con `dict(...)`; `test_U6_la_instantanea_es_una_copia_y_no_una_referencia`. |
| Una entrada inválida sobrescribe o borra el historial. | La instantánea se guarda solo después de todas las validaciones; `test_U6_entrada_invalida_preserva_el_historial`, `test_U6_elegir_en_un_final_no_borra_el_historial` (agregada tras detectar con una mutación manual que faltaba cubrir ese caso). |
| Reiniciar deja un retroceso «fantasma» hacia la partida anterior. | `reiniciar()` pone `_anterior = None`; `test_U5_extendido_*`. |
| Romper comportamiento de la versión inicial. | Las 95 pruebas de `v1-inicial` siguen pasando sin debilitar ninguna aserción (solo se agregaron pruebas). |
| Conflicto con el comando `d` si una historia usa `d` como ID de opción. | Se documenta en Limitaciones del README; la opción sigue disponible por número. |
| Falta de tiempo antes del cierre. | Cambio pequeño y aislado en `sesion.py`/`cli.py` gracias a la separación de capas (AD-2). |

## 5. Evidencia de funcionamiento

- Pruebas: `python -m pytest -v` → **148 pasan, 0 fallan** (`evidencias/resultados_pruebas.txt`), incluidas las 12 ejecuciones de `test_U6_*` y las extensiones de U5 e I1.
- RNF: `python scripts/verificar_rnf.py` → los tres CUMPLE (`evidencias/rnf/resultado_rnf.txt`).
- Etiquetas: `v1-inicial` (antes) y `v2-cambio` (después); historial en `evidencias/historial_git.txt`.
- Demostración: en el video [COMPLETAR: minuto en que se muestra deshacer] se reproduce el ejemplo del docente: `revisar`, `investigar`, `d`, `d`, `continuar`.
