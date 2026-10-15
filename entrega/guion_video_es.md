# Guion del video — solo rótulos (sin voz)

Guía completa para grabar la demostración a partir de un clon nuevo del repositorio. Duración objetivo: **± 5:30** (máximo permitido: 6:00).

Este archivo es solo de apoyo y no se incluye en el ZIP; del directorio `entrega/` solo se empaqueta `entrega/video.mp4`.

**Cómo leer el guion**
- Columna **Escribir / hacer**: lo que se teclea o se hace durante la grabación.
- **⏸**: pausa de 4–5 segundos sin teclear, para dar tiempo a leer el rótulo.
- Los textos en cita (**R1, R2, …**) son los rótulos. Se copian tal cual en Clipchamp, sobre ese momento del video.

---

## 1. Requisitos previos (una sola vez)

- Windows 10 u 11 con PowerShell.
- **Git**: <https://git-scm.com>.
- **Python 3.10 o superior**: <https://www.python.org>. Durante la instalación, marcar «Add python.exe to PATH».
- **Herramienta Recortes** (Snipping Tool) actualizada y **Clipchamp**. Ambas vienen con Windows 11; si faltan, se instalan desde Microsoft Store.
- Visual Studio Code (opcional), para mostrar `docs/arquitectura.md` en el segmento 6.

## 2. Clonar e instalar

```powershell
git clone https://github.com/jaimeutb/parcial-ultima-transmision.git
cd parcial-ultima-transmision
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # solo si Activate.ps1 está bloqueado
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

El clon incluye las etiquetas `v1-inicial` y `v2-cambio`, que se usan en el segmento 6.

## 3. Verificar antes de grabar (no se graba)

```powershell
python -m pytest -q                                  # debe terminar con «301 passed»
python -m motor --validar historias/el_faro.json     # «Historia válida: …»
git tag                                              # v1-inicial y v2-cambio
```

Si algo falla, no grabar todavía. Hacer un ensayo completo del guion sin grabar.

## 4. Preparar la pantalla

Abrir una terminal de PowerShell **nueva** en la carpeta del proyecto y ejecutar:

```powershell
.venv\Scripts\Activate.ps1
function prompt { "PS> " }    # indicador corto; oculta la ruta local
cls
```

- Ajustar la ventana de la terminal para que ocupe solo el **± 80 % superior de la pantalla**. La franja inferior queda libre para los rótulos.
- Aumentar el tamaño de letra de la terminal (Ctrl + «+» o Ctrl + rueda del ratón) hasta que se lea bien a pantalla completa.
- Activar **No molestar** (Win+N) y cerrar las demás ventanas.
- Dejar abierto en VS Code `docs/arquitectura.md`, en la sección **AD-2** (vista previa: Ctrl+Shift+V).
- Iniciar la grabación: **Win+Shift+R** → seleccionar toda la pantalla → **Iniciar**, con el micrófono desactivado.

---

## 5. Guion

### Segmento 0 — Presentación (0:00–0:15)

| Escribir / hacer | Rótulo |
|---|---|
| Terminal vacía ⏸⏸ | R1, luego R2 |

> **R1** (8 s) — Parcial práctico de Ingeniería de Software · «La última transmisión»
> JAIME MO CHEN · Curso 1206 · Docente: Aisner Jose Marrugo Juliao

> **R2** (6 s) — Motor de historias interactivas en Python (consola). Se muestran: tres finales, segunda historia, validación, pruebas y deshacer.

### Segmento 1 — Tres finales y condiciones (0:15–1:40)

| Escribir / hacer | Rótulo |
|---|---|
| `python -m motor historias/la_ultima_transmision.json` ⏸ | R3 |
| `revisar`, `investigar` | R4 |
| `e` ⏸ | R5 |
| (señalar las opciones de E3) ⏸ | R6 |
| `activar_codigo` ⏸ | R7 |
| `r` | R8 |
| `revisar`, `continuar` ⏸⏸ | R9 |
| `activar_sin_verificar` ⏸ | R10 |
| `r`, `revisar`, `continuar`, `cortar` ⏸ | R11 |

> **R3** — Historia oficial cargada desde un archivo JSON. Solo se muestran las opciones habilitadas.

> **R4** — Se eligió «investigar»: su efecto asigna conoce_origen = verdadero.

> **R5** — Comando «e»: muestra el estado actual de las variables.

> **R6** — Condición: como conoce_origen es verdadero, E3 ofrece «activar_codigo».

> **R7** — Final 1 de 3: E4 Rescate.

> **R8** — «r» reinicia la partida con las variables iniciales.

> **R9** (7 s) — Ahora sin investigar (conoce_origen = falso): E3 ofrece «activar_sin_verificar» en lugar de «activar_codigo».

> **R10** — Final 2 de 3: E5 El eco.

> **R11** — Final 3 de 3: E6 Silencio. «cortar» está disponible se haya investigado o no.

### Segmento 2 — Deshacer, solicitud de cambio de la hora 6 (1:40–2:50)

Continuar en la misma partida. **Anotar el minuto en que empieza este segmento**: se necesita en `docs/analisis_impacto_cambio.md`.

| Escribir / hacer | Rótulo |
|---|---|
| ⏸ | R12 |
| `r`, `revisar`, `investigar`, `e` ⏸ | R13 |
| `d`, `e` ⏸ | R14 |
| `d` ⏸ | R15 |
| `continuar` ⏸⏸ | R16 |
| `activar_sin_verificar`, `d` ⏸ | R17 |
| `q` | — |

> **R12** — Solicitud de cambio (hora 6): deshacer la última elección válida, con un solo nivel.

> **R13** — Ejemplo del docente: desde E2, «investigar» lleva a E3 con conoce_origen = verdadero.

> **R14** — «d» deshace: vuelve a E2 y conoce_origen vuelve a falso.

> **R15** — Un segundo «d» no cambia nada: solo se guarda un nivel.

> **R16** (7 s) — Al continuar sin investigar, E3 muestra «activar_sin_verificar» y «cortar», como pide la solicitud.

> **R17** — Desde un final, «d» también vuelve a E3 con los valores previos.

### Segmento 3 — Segunda historia (2:50–3:30)

| Escribir / hacer | Rótulo |
|---|---|
| `cls` y luego `python -m motor historias/el_faro.json` ⏸ | R18 |
| `faro_buscar_llave` ⏸ | R19 |
| `faro_abrir_candado`, `faro_encender_lampara` ⏸ | R20 |
| `q` | — |

> **R18** (7 s) — Segunda historia, «El faro de Isla Gris», con el mismo motor: no se modificó el código de motor/.

> **R19** — Con la llave se habilita «faro_abrir_candado»; si se va directo a la puerta, esa opción no aparece.

> **R20** — Final «faro_rescate» alcanzado.

### Segmento 4 — Error de destino inexistente (3:30–3:55)

| Escribir / hacer | Rótulo |
|---|---|
| `cls` y luego `python -m motor --validar historias/invalidas/destino_inexistente.json` ⏸ | R21 |
| `$LASTEXITCODE` ⏸ | R22 |

> **R21** — Archivo inválido: una opción apunta a la escena E99, que no existe.

> **R22** (7 s) — El validador informa código, ubicación y causa, no abre ninguna partida y termina con código 2.

### Segmento 5 — Pruebas (3:55–4:35)

| Escribir / hacer | Rótulo |
|---|---|
| `cls` y luego `python -m pytest -q` ⏸ | R23 |
| `python -m pytest -v tests/test_deshacer.py` ⏸⏸ | R24 |

> **R23** (7 s) — Pruebas automatizadas: 301 pasan (U1–U6, I1, CLI, RNF y coherencia de la documentación).

> **R24** (7 s) — Las 12 pruebas U6 del cambio: ejemplo del docente, un solo nivel, entradas inválidas y deshacer desde cada final.

### Segmento 6 — Cierre: arquitectura e impacto del cambio (4:35–5:35)

| Escribir / hacer | Rótulo |
|---|---|
| Pasar a VS Code: `docs/arquitectura.md`, sección AD-2 ⏸⏸⏸ | R25, R26, R27 |
| Volver a la terminal: `cls` y luego `git diff --stat v1-inicial v2-cambio -- motor/` ⏸⏸⏸ | R28, R29 |
| ⏸ | R30 |
| Detener la grabación | — |

> **R25** — Decisión de arquitectura AD-2: deshacer con una única instantánea (escena + copia de las variables).

> **R26** — Alternativas descartadas: pila de instantáneas, patrón Command y repetir las elecciones desde el inicio.

> **R27** (7 s) — Motivo: la regla «un solo nivel» se cumple por construcción y no se tocan el modelo, el validador ni las historias.

> **R28** (7 s) — Impacto del cambio: RF17 nuevo; RF06, RF08, RF09 y RF16 ampliados; modelos, trazabilidad y backlog actualizados.

> **R29** (7 s) — Entre v1-inicial y v2-cambio solo cambiaron motor/sesion.py y motor/cli.py. Las 95 pruebas de la versión inicial siguen pasando.

> **R30** — Fin de la demostración.

---

## 6. Editar en Clipchamp

1. Abrir **Clipchamp** → **Crear un nuevo video** → importar el MP4 de la grabación (la Herramienta Recortes lo guarda normalmente en la carpeta **Videos**) y arrastrarlo a la línea de tiempo.
2. Cortar pausas demasiado largas o errores de tecleo: colocar el cursor, pulsar **S** (dividir) y eliminar el fragmento.
3. En el panel izquierdo, **Texto** → elegir un estilo simple → arrastrarlo a la línea de tiempo **encima** del video, alineado con su momento → pegar el rótulo.
4. Formato: letra blanca sobre fondo oscuro semitransparente, tamaño grande, en la **franja inferior** libre. Duración según el guion (5 s si no se indica otra).
5. **Exportar** → **1080p**. Comprobar que el video dure como máximo 6:00 y que el texto se lea a pantalla completa.

## 7. Después de grabar

1. Guardar el video dentro del proyecto como `entrega\video.mp4`:

   ```powershell
   New-Item -ItemType Directory -Force entrega | Out-Null
   Move-Item "RUTA\DEL\VIDEO_EXPORTADO.mp4" entrega\video.mp4
   ```

   `entrega/*.mp4` está en `.gitignore`: el video no se sube a GitHub, pero `scripts/empaquetar.py` lo incluye en el ZIP. Por eso el ZIP debe crearse en el mismo equipo donde está el video.

   Alternativa: subirlo a Google Drive o a YouTube (como «no listado»), dar acceso a «cualquier persona con el enlace» y probar el enlace en una ventana de incógnito.

2. Completar los `[COMPLETAR]` relacionados con el video:
   - `README.md`, sección «Demostración en video»: «`entrega/video.mp4` (incluido en el ZIP)» o el enlace.
   - `docs/informe.md`, fila «Video» de la identificación.
   - `docs/analisis_impacto_cambio.md`, línea «Demostración»: minuto en que empieza el segmento 2.
   - `docs/backlog.md`, ítem B22: estado «Hecho».

3. Regenerar los PDF (requiere Chrome o Edge y conexión a internet):

   ```powershell
   pip install -r requirements-docs.txt
   python scripts/generar_pdfs.py
   ```

4. Hacer commit de los documentos actualizados.

5. Revisar el paquete sin crearlo:

   ```powershell
   python scripts/empaquetar.py --simular MoJaime
   ```

   El nombre usa el primer apellido y el primer nombre, sin espacios ni tildes.
