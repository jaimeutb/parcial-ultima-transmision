# Requisitos — Motor de historias «La última transmisión»

Vocabulario común con el código: **Historia**, **Escena**, **Opcion**, **Sesion**, `condiciones`, `efectos`, `destino`, **ErrorContenido**.
Cada RF indica comportamiento observable, necesidad vinculada y criterio de aceptación (Dado / Cuando / Entonces).
La trazabilidad completa (modelo, archivo, prueba, evidencia) está en [trazabilidad.md](trazabilidad.md).

## 1. Requisitos funcionales

### Versión inicial (`v1-inicial`)

| ID | Requisito (comportamiento observable) | Necesidad |
|---|---|---|
| RF01 | El sistema carga una historia desde un archivo JSON independiente indicado por su ruta; cada relato vive en su propio archivo. | N01 |
| RF02 | Al iniciar una partida, la sesión se sitúa en la escena `inicio` con los valores de `variables` declarados en el archivo. | N01 |
| RF03 | La interfaz muestra el título, el texto de la escena actual y sus opciones habilitadas numeradas, con su `id`. | N02 |
| RF04 | Solo se ofrecen las opciones cuyas `condiciones` se cumplen todas con el estado actual; un mapa de condiciones vacío habilita la opción. | N02 |
| RF05 | Al elegir una opción habilitada (por número o por `id`), se aplican todos sus `efectos` y la partida pasa a su `destino`. | N03 |
| RF06 | Una opción inexistente en la escena o no habilitada se rechaza con un mensaje y no modifica ni la escena ni las variables, aunque su `id` se envíe directamente al motor. | N03 |
| RF07 | La sesión conserva los valores de las variables durante toda la partida y evalúa las condiciones posteriores con ellos; el lector puede consultarlos (`e`). | N04 |
| RF08 | Al llegar a una escena `final`, se muestra «FIN», no se ofrecen opciones y cualquier elección se rechaza (`PARTIDA_FINALIZADA`). | N05 |
| RF09 | Reiniciar devuelve la partida a la escena `inicio` y a las variables iniciales, sin conservar información de la partida anterior. | N05 |
| RF10 | Se rechaza un archivo inexistente, ilegible, que no es JSON válido, sin campos obligatorios o con campos de tipo incorrecto (`ARCHIVO_ILEGIBLE`, `ESTRUCTURA_INVALIDA`, `CAMPO_FALTANTE`). | N06 |
| RF11 | Se rechaza un `inicio` o un `destino` que no corresponde a ninguna escena (`INICIO_INEXISTENTE`, `DESTINO_INEXISTENTE`). | N06 |
| RF12 | Se rechazan IDs de escena repetidos en la historia e IDs de opción repetidos dentro de una misma escena (`ESCENA_DUPLICADA`, `OPCION_DUPLICADA`). | N06 |
| RF13 | Se rechazan `condiciones` o `efectos` que usan variables no declaradas y cualquier valor no booleano en `variables`, `condiciones` o `efectos` — `0`, `1`, `"true"` no son booleanos (`VARIABLE_NO_DECLARADA`, `VALOR_NO_BOOLEANO`). | N06 |
| RF14 | Se rechaza una escena final con opciones o una escena no final sin opciones (`OPCIONES_INCOMPATIBLES_CON_FINAL`). | N06 |
| RF15 | La validación completa ocurre antes de abrir cualquier sesión: se informan **todos** los errores, cada uno con código, causa en español y ubicación (ruta del campo + ID de escena/opción); no se abre la partida, el programa termina con código 2 y nunca muestra un traceback. `--validar` permite al escritor comprobar el archivo sin jugar. | N06 |
| RF16 | Si durante la partida una escena no final queda sin opciones habilitadas, se informa «No hay opciones disponibles en esta escena» y se permite reiniciar. | N03, N05 |

### Agregado por la solicitud de cambio (hora 6, `v2-cambio`)

| ID | Requisito (comportamiento observable) | Necesidad |
|---|---|---|
| RF17 | El lector puede **deshacer su última elección válida**: se restauran exactamente la escena y todas las variables previas a esa elección. Solo hay un nivel de retroceso, que se consume al usarlo y se recupera con una nueva elección válida. Al comenzar y tras reiniciar no hay retroceso. Las entradas inválidas no modifican la sesión ni el historial. Funciona desde un final y desde una escena bloqueada. **Reemplaza el acuerdo provisional «sin retroceso»** de la versión inicial (ver §4). | N03, N04, N05 |

## 2. Criterios de aceptación

| ID | Dado | Cuando | Entonces |
|---|---|---|---|
| RF01 | el archivo `historias/el_faro.json` | se ejecuta `python -m motor historias/el_faro.json` | se muestra «El faro de Isla Gris» y la escena `faro_muelle`. |
| RF02 | la historia oficial | se crea una sesión | la escena es E1 con `conoce_origen` = falso y `confia_en_la_voz` = falso. |
| RF03 | una partida en E2 | se muestra la escena | aparecen su texto y `1) Investigar archivo [investigar]`, `2) Continuar sin investigar [continuar]`. |
| RF04 (CA01) | una partida nueva | se elige revisar e investigar | la sesión está en E3 con `conoce_origen` verdadero y se muestran exactamente `activar_codigo` y `cortar`. |
| RF05 | la sesión en E2 | se elige `investigar` (o `1`) | la escena es E3 y `conoce_origen` = verdadero. |
| RF06 (CA02) | E3 sin conocer el origen | se envía `activar_codigo` directamente a `Sesion.elegir` | se devuelve `OPCION_NO_HABILITADA`, escena y variables no cambian, y `activar_sin_verificar` lleva a E5. |
| RF07 | revisar → investigar → (E3) | se consultan las variables o se elige en E3 | `conoce_origen` sigue verdadero y habilita `activar_codigo`. |
| RF08 | la sesión en E4, E5 o E6 | se muestra la escena o se intenta elegir | se muestra «FIN», hay 0 opciones y elegir devuelve `PARTIDA_FINALIZADA` sin cambios. |
| RF09 | una partida en E4 con `conoce_origen` verdadero | se reinicia y se continúa sin investigar | la escena es E1 con valores iniciales y en E3 aparece `activar_sin_verificar`. |
| RF10 | un archivo con JSON roto, sin `titulo` o con `escenas` que no es lista | se carga | se rechaza con `ARCHIVO_ILEGIBLE` / `CAMPO_FALTANTE` / `ESTRUCTURA_INVALIDA` y el nombre del archivo o campo. |
| RF11 (CA03) | una copia de la historia con destino `E99` | se carga | se rechaza con `DESTINO_INEXISTENTE` mencionando `E99`, la opción `investigar` y la escena E2, sin abrir sesión. |
| RF12 | una historia con dos escenas `E4` o dos opciones `investigar` en E2 | se carga | se rechaza con `ESCENA_DUPLICADA` / `OPCION_DUPLICADA` y el ID repetido. |
| RF13 | una condición con `tiene_mapa` no declarada o un valor `"true"` | se carga | se rechaza con `VARIABLE_NO_DECLARADA` / `VALOR_NO_BOOLEANO` y el nombre de la variable. |
| RF14 | E4 con una opción o E1 sin opciones | se carga | se rechaza con `OPCIONES_INCOMPATIBLES_CON_FINAL` y el ID de la escena. |
| RF15 | un archivo con tres defectos distintos | se ejecuta `python -m motor --validar <archivo>` | se listan los tres errores con código, causa y ubicación, el proceso termina con código 2 y la salida no contiene «Traceback». |
| RF16 | una escena no final cuyas opciones requieren una variable que es falsa | la partida llega a ella | `esta_bloqueada` es verdadero, se informa el bloqueo y `r` vuelve al inicio. |
| RF17.1 Restauración | E2 con `conoce_origen` falso | se elige `investigar` (E3, verdadero) y se deshace | la escena es E2 y `conoce_origen` = falso (ejemplo del docente). |
| RF17.2 Un solo nivel | se acaba de deshacer | se intenta deshacer otra vez | se devuelve `SIN_RETROCESO` y nada cambia; tras `continuar`, E3 muestra `activar_sin_verificar` y `cortar`; una nueva elección vuelve a habilitar deshacer. |
| RF17.3 Inicio y reinicio | una sesión nueva, o una partida avanzada que se reinicia | se intenta deshacer | `puede_deshacer` es falso y se devuelve `SIN_RETROCESO`. |
| RF17.4 Entrada inválida | E3 tras investigar | se elige un ID inexistente o no habilitado y luego se deshace | la entrada se rechaza sin cambios y deshacer vuelve a E2 con los valores previos. |
| RF17.5 Desde un final | la partida en E4, E5 o E6 | se deshace | se vuelve a E3 con los valores previos a la última elección (p. ej., E4 → E3 con `conoce_origen` verdadero y `confia_en_la_voz` falso). |

## 3. Requisitos no funcionales

| ID | Atributo | Métrica y meta | Procedimiento de verificación | Evidencia |
|---|---|---|---|---|
| RNF-01 | Modificabilidad del contenido | Una historia nueva (≥ 3 escenas, ≥ 1 condición, ≥ 1 efecto) se juega hasta el **100 %** de sus finales con **0 líneas** cambiadas en `motor/`; **0** IDs de escena/opción como literal y **0** nombres de variable de las historias en `motor/*.py`. | (a) exploración automática de todos los estados alcanzables de `el_faro.json` con `Sesion`; (b) búsqueda por expresiones regulares en `motor/*.py`; (c) `git show --numstat` de los commits que agregaron `el_faro.json`. | `tests/test_rnf.py::test_RNF01_*`, `evidencias/rnf/resultado_rnf.txt` |
| RNF-02 | Claridad de errores | **100 %** de los 10 códigos de error producen un mensaje en español con la causa y el ID o campo implicado; código de salida 2; **0** tracebacks. | `python -m motor --validar` en un subproceso para 21 archivos inválidos (≥ 1 por código) y comprobación de código, ID/campo y ausencia de «Traceback». | `tests/test_rnf.py::test_RNF02_*`, `tests/test_validacion.py::test_U4_*`, `evidencias/rnf/resultado_rnf.txt` |
| RNF-03 | Confiabilidad | En 1 000 secuencias aleatorias (semilla fija) de 50 acciones por historia — IDs válidos, IDs de otras escenas, texto aleatorio, deshacer, reiniciar —: **0** excepciones no controladas y **0** violaciones de invariantes (la escena existe, las claves de variables son las declaradas, todos los valores son booleanos, un final no tiene opciones habilitadas, una acción rechazada no cambia el estado). | `secuencias_aleatorias()` en `scripts/verificar_rnf.py`, ejecutada por la prueba y por el script. | `tests/test_rnf.py::test_RNF03_*`, `evidencias/rnf/resultado_rnf.txt` |

## 4. Preguntas de aclaración, respuestas y supuestos

| # | Pregunta | Respuesta o supuesto |
|---|---|---|
| P1 | La escritora quiere poder retroceder siempre; el diseñador quiere decisiones irreversibles. ¿Se permite retroceder? | **Acuerdo provisional** (guía): la versión inicial no implementa retroceso; se documenta el conflicto. **Resolución posterior**: la solicitud de cambio de la hora 6 decide un retroceso de **un solo nivel** (RF17). [COMPLETAR: indicar si enviaron esta pregunta al docente, cuándo y qué respondió; si no hubo respuesta, dejar «sin respuesta dentro de la ventana».] |
| P2 | ¿En qué formato escribirán los escritores las historias? | **Supuesto**: JSON con el contrato de referencia de la guía, porque el archivo oficial ya usa ese formato y Python lo lee con la biblioteca estándar. El README explica el formato para quien no programa. [COMPLETAR si hubo respuesta del docente.] |
| P3 | ¿Qué debe ocurrir si en una escena no final ninguna opción queda habilitada? | **Supuesto** compatible con la guía: informar el bloqueo y permitir reiniciar (RF16). Tras el cambio también se puede deshacer. No se analiza automáticamente cada camino del relato (fuera de alcance según la guía). [COMPLETAR si hubo respuesta.] |

Supuestos menores adicionales: los IDs distinguen mayúsculas y minúsculas; `condiciones` y `efectos` son obligatorios aunque estén vacíos (`{}`), igual que en el archivo oficial; si un `id` de opción coincide con un comando de la consola (`r`, `q`, `d`, `e`, `?`), se elige por número.

## 5. Conflicto escritora vs. diseñador y su resolución

- **Conflicto**: la escritora pide retroceder siempre (explorar sin perder el trabajo); el diseñador pide decisiones irreversibles (que las consecuencias pesen).
- **Versión inicial**: se registró el acuerdo provisional de no implementar retroceso y se formuló la pregunta P1, sin presuponer la decisión.
- **Resolución (solicitud de cambio, hora 6)**: el cliente decide un punto intermedio: deshacer **solo la última** elección válida, revirtiendo todas sus consecuencias, sin rehacer y sin retroceso ilimitado. Satisface a la escritora (se puede corregir un error inmediato) y conserva el peso de las decisiones para el diseñador (no se puede volver atrás varias veces). Se implementó como RF17.

## 6. Defecto detectado en revisión cruzada

[COMPLETAR: describir el defecto o la ambigüedad que encontró un integrante al revisar los requisitos del otro, quién lo encontró y cómo se corrigió. Deben confirmar el candidato siguiente o reemplazarlo por el que realmente detectaron.]

**Candidato sugerido (confirmar o reemplazar):** una primera redacción de RF06 decía «el sistema ignora las opciones inválidas». Es ambigua: no dice si el estado cambia, si el lector recibe un mensaje, ni si cubre un `id` que existe pero no está habilitado y se envía directamente al motor (CA02). **Corrección**: RF06 especifica que la opción inexistente **o no habilitada** se rechaza con mensaje, que escena y variables quedan idénticas y que la regla se aplica en `Sesion.elegir`, no solo en la interfaz; se agregó el criterio CA02 y la prueba `test_U3_CA02_activar_codigo_sin_conocer_origen_se_rechaza`.
