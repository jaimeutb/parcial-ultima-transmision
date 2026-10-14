"""Genera docs/anexo.md a partir de los diagramas y la matriz, para no duplicar contenido a mano.

Uso:  python scripts/generar_anexo.py   (ejecutarlo de nuevo si cambian modelos, arquitectura o trazabilidad)
"""
from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


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
    partes += [
        "", "## D. Tablero",
        "", "### D.1 Captura inicial",
        "", "[COMPLETAR: insertar `evidencias/tablero/tablero_inicial.png` (fecha y hora visibles)]",
        "", "### D.2 Captura final",
        "", "[COMPLETAR: insertar `evidencias/tablero/tablero_final.png` (fecha y hora visibles)]",
        "",
    ]
    (DOCS / "anexo.md").write_text("\n".join(partes), encoding="utf-8")
    print("docs/anexo.md generado")


if __name__ == "__main__":
    main()
