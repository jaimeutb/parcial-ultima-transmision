"""Genera docs/anexo.md a partir de los diagramas y la matriz, para no duplicar contenido a mano.

Uso:  python scripts/generar_anexo.py   (ejecutarlo de nuevo si cambian modelos, arquitectura o trazabilidad)
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
TABLERO = DOCS.parent / "evidencias" / "tablero"
CAPTURAS = [("tablero_inicial", "Captura inicial"), ("tablero_final", "Captura final")]
NOTA_TABLERO = (
    "Tablero en Trello con los ítems de `docs/backlog.md` (trabajo individual: todas las tarjetas a cargo del autor). "
    "El tablero se creó al final del trabajo, a partir del backlog: la captura inicial muestra el estado de partida "
    "**reconstruido** (todos los ítems en «Por hacer»), no una captura tomada al comenzar el parcial. "
    "Las fechas indicadas son las de los archivos de captura."
)


def seccion_captura(nombre: str) -> str:
    """Inserta la captura si existe (png/jpg) con su fecha de archivo; si no, deja el marcador pendiente."""
    for extension in (".png", ".jpg", ".jpeg"):
        ruta = TABLERO / f"{nombre}{extension}"
        if ruta.exists():
            fecha = dt.datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            return f"![{nombre}](../evidencias/tablero/{ruta.name})\n\n*Archivo `{ruta.name}`, capturado el {fecha}.*"
    return f"[COMPLETAR: guardar `evidencias/tablero/{nombre}.png` y volver a ejecutar este script]"


def bloques_mermaid(texto: str) -> list[tuple[str, str]]:
    """Devuelve (título de la sección ##, bloque mermaid) en orden de aparición."""
    resultado, titulo = [], ""
    for parte in re.split(r"(?m)^(## .*)$", texto):
        if parte.startswith("## "):
            titulo = parte[3:].strip()
        for bloque in re.findall(r"```mermaid\n.*?```", parte, flags=re.S):
            resultado.append((titulo, bloque))
    return resultado


def main() -> None:
    modelos = bloques_mermaid((DOCS / "modelos.md").read_text(encoding="utf-8"))
    arquitectura = bloques_mermaid((DOCS / "arquitectura.md").read_text(encoding="utf-8"))[:1]
    matriz = (DOCS / "trazabilidad.md").read_text(encoding="utf-8").split("\n", 1)[1]

    partes = [
        "# Anexo — Diagramas, matriz de trazabilidad y tablero",
        "",
        "Referenciado desde el informe. Contiene solo diagramas, la matriz y las capturas del tablero.",
        "Generado con `python scripts/generar_anexo.py` desde `docs/modelos.md`, `docs/arquitectura.md` y `docs/trazabilidad.md`.",
        "",
        "## A. Modelos",
    ]
    for numero, (titulo, bloque) in enumerate(modelos, start=1):
        partes += ["", f"### A.{numero} {re.sub(r'^[0-9]+[.] ', '', titulo)}", "", bloque]
    partes += ["", "## B. Arquitectura: componentes y capas", "", arquitectura[0][1]]
    partes += ["", "## C. Matriz de trazabilidad", matriz.strip().replace("\n## ", "\n### C. ")]
    partes += ["", "## D. Tablero", "", NOTA_TABLERO]
    for numero, (archivo, titulo) in enumerate(CAPTURAS, start=1):
        partes += ["", f"### D.{numero} {titulo}", "", seccion_captura(archivo)]
    partes.append("")
    (DOCS / "anexo.md").write_text("\n".join(partes), encoding="utf-8")
    print("docs/anexo.md generado")


if __name__ == "__main__":
    main()
