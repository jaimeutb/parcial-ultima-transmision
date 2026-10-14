# Solicitud de cambio del parcial — La última transmisión

> Transcripción del documento publicado por el docente a la hora 6. El PDF original
> se descarga del aula virtual y se conserva en `enunciado/` junto a la guía.
> [COMPLETAR: confirmar que esta transcripción coincide con el PDF descargado de Savio y anotar la hora real en que lo descargaron.]

Material para entregar al cumplirse la hora 6. El cierre del parcial se mantiene en la hora 12.

## Nueva decisión del cliente

El colectivo ha acordado que el lector debe poder deshacer su última decisión. Al hacerlo, también deben revertirse todas sus consecuencias. Esta solicitud reemplaza el acuerdo provisional de no implementar retroceso.

| Regla | Comportamiento obligatorio |
|---|---|
| Restauración | Deshacer restaura exactamente la escena y todas las variables anteriores a la última elección válida. |
| Un solo nivel | Después de deshacer, no se permite otro retroceso hasta realizar una nueva elección válida. No se exige rehacer. |
| Inicio y reinicio | Al comenzar no hay retroceso disponible. Reiniciar elimina el historial y restaura el estado inicial. |
| Entrada inválida | Una opción inexistente o no habilitada no modifica la sesión ni sustituye el historial de la última elección válida. |
| Desde un final | Es posible deshacer desde E4, E5 o E6; se regresa a E3 y se restauran los valores previos a esa elección. |

## Trabajo y evidencia

Conserven la versión disponible al recibir la solicitud, aunque esté incompleta. Redacten el nuevo requisito con su propio identificador y aceptación; analicen el impacto; actualicen backlog, modelos, código, pruebas y trazabilidad. No se exige una arquitectura o patrón específico para resolverlo.

## Ampliación de pruebas

Añadan U6: deshacer restaura escena y variables y consume la posibilidad de retroceder. Usen variantes para comprobar que una entrada inválida preserva el historial y que una nueva elección vuelve a habilitar un retroceso. Extiendan U5 para verificar que reiniciar elimina el historial, e I1 para deshacer desde un final después de cargar el archivo y recorrer la historia.

Ejemplo: desde E2, investigar lleva a E3 con conoce_origen verdadero. Deshacer devuelve a E2 con conoce_origen falso. Un segundo intento de deshacer no cambia nada. Al continuar sin investigar, E3 muestra activar sin verificar y cortar comunicación.

Incluyan el resultado en el informe y la demostración ya solicitados. Este anexo no agrega páginas obligatorias ni un video adicional. Su evaluación corresponde a los 4 puntos de comportamiento nuevo y pruebas dentro del criterio de cambio; análisis y trazabilidad conservan sus pesos publicados.
