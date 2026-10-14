# Backlog del producto

Prioridad: **A** imprescindible para la entrega · **M** necesaria · **B** deseable.
Estado al etiquetar `v2-cambio`. Trabajo individual: el responsable de todos los ítems es el autor, [COMPLETAR: nombre] (usuario Git `jaimeutb`); debe coincidir con el tablero.
Los ítems marcados **🕕 hora 6** se agregaron al recibir la solicitud de cambio.

| ID | Ítem | RF / RNF | Prioridad | Responsable | Estado | Evidencia |
|---|---|---|---|---|---|---|
| B01 | Definir problema, actores, alcance, riesgos y atributos de calidad | — | A | Autor | Borrador | `docs/informe.md` §2 |
| B02 | Redactar RF (N01–N06), RNF y preguntas | RF01–RF16, RNF-01..03 | A | Autor | Hecho (borrador a revisar) | `docs/requisitos.md` |
| B03 | Revisión cruzada de requisitos y registro del defecto | — | A | Autor | Pendiente | `docs/requisitos.md` §6 |
| B04 | Modelos: contexto, casos de uso, clases, secuencia, estados | — | A | Autor | Hecho | `docs/modelos.md` |
| B05 | Arquitectura y dos decisiones | — | A | Autor | Hecho | `docs/arquitectura.md` |
| B06 | Modelo inmutable y cargador con errores controlados | RF01, RF10 | A | Autor | Hecho | `motor/modelo.py`, `motor/cargador.py` |
| B07 | Validador con los 10 códigos de error | RF10–RF15 | A | Autor | Hecho | `motor/validador.py` |
| B08 | Sesión: condiciones, efectos, rechazo, finales, reinicio, bloqueo | RF02, RF04–RF09, RF16 | A | Autor | Hecho | `motor/sesion.py` |
| B09 | Interfaz de consola y `--validar` | RF03, RF15 | A | Autor | Hecho | `motor/cli.py` |
| B10 | Segunda historia sin cambiar el motor | RNF-01 | A | Autor | Hecho | `historias/el_faro.json` |
| B11 | Pruebas U1–U5, I1 y bloqueo | — | A | Autor | Hecho | `tests/test_sesion.py`, `test_validacion.py`, `test_integracion.py` |
| B12 | Guardar versión inicial (`v1-inicial`) | — | A | Autor | Hecho | etiqueta `v1-inicial` |
| B13 🕕 hora 6 | Analizar el impacto de la solicitud de cambio | RF17 | A | Autor | Hecho | `docs/analisis_impacto_cambio.md` |
| B14 🕕 hora 6 | Redactar RF17 y actualizar requisitos y modelos | RF17 | A | Autor | Hecho | `docs/requisitos.md`, `docs/modelos.md` |
| B15 🕕 hora 6 | Implementar deshacer (sesión + CLI) | RF17 | A | Autor | Hecho | `motor/sesion.py::deshacer`, `motor/cli.py` |
| B16 🕕 hora 6 | Pruebas U6 y extensiones de U5 e I1 | RF17 | A | Autor | Hecho | `tests/test_deshacer.py` |
| B17 🕕 hora 6 | Actualizar trazabilidad y backlog | RF17 | A | Autor | Hecho | `docs/trazabilidad.md` |
| B18 | Verificación de RNF con script reproducible | RNF-01..03 | A | Autor | Hecho | `scripts/verificar_rnf.py`, `evidencias/rnf/` |
| B19 | README con instalación, ejecución, formato y rutas | — | A | Autor | Hecho (faltan nombres y enlace) | `README.md` |
| B20 | Informe y anexo en PDF | — | A | Autor | Pendiente (exportar) | `docs/informe.md`, `docs/anexo.md` |
| B21 | Capturas del tablero inicial y final | — | A | Autor | Pendiente | `evidencias/tablero/` |
| B22 | Video de demostración ≤ 6 min | — | A | Autor | Pendiente | `entrega/video.mp4` o enlace en README |
| B23 | Empaquetar ZIP y subirlo a Savio | — | A | Autor | Pendiente | `scripts/empaquetar.py` |
| B24 | Comando `e`/estado para ver variables en la demostración | RF07 | B | Autor | Hecho | `motor/cli.py::Consola.mostrar_estado` |
| B25 | Menú para elegir historia si no se pasa ruta | RF01 | B | Autor | Hecho | `motor/cli.py::elegir_historia` |

## Definición de terminado (DoD)

Un ítem está **terminado** cuando:

1. Su comportamiento está descrito en un RF/RNF con criterio de aceptación (si es funcional).
2. El código está en `motor/` sin IDs ni variables de ninguna historia concreta (lo verifica `test_RNF01_el_motor_no_contiene_ids_ni_variables_de_las_historias`).
3. Tiene al menos una prueba automatizada con aserciones reales, y `python -m pytest` pasa completo sin debilitar aserciones existentes.
4. Ningún error llega al usuario como traceback; los mensajes están en español.
5. Los modelos, la trazabilidad y el README reflejan el cambio con los mismos nombres que el código.
6. Está en un commit pequeño cuyo mensaje cita el RF o la prueba (p. ej., `RF17: …`).
7. [COMPLETAR/confirmar] El autor relee el cambio y su prueba en una segunda pasada antes de marcarlo «hecho» (sustituye la revisión entre integrantes en el trabajo individual).
