"""Exporta docs/informe.md y docs/anexo.md a PDF (A4) con los diagramas Mermaid dibujados.

Uso:  pip install -r requirements-docs.txt
      python scripts/generar_pdfs.py
Necesita Google Chrome o Microsoft Edge instalados y conexión a internet (carga mermaid.js desde jsDelivr).
Volver a ejecutarlo después de completar los [COMPLETAR] o de cambiar los documentos.
"""
from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
DOCUMENTOS = ["informe", "anexo"]
NAVEGADORES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "msedge",
]

ESTILO = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.38; color: #111; }
h1 { font-size: 17pt; margin: 0 0 8pt; } h2 { font-size: 13pt; margin: 14pt 0 5pt; border-bottom: 1px solid #999; }
h3 { font-size: 11.5pt; margin: 10pt 0 4pt; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #888; padding: 2.5pt 4pt; vertical-align: top; text-align: left; }
th { background: #e8e8e8; } tr { page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 8.8pt; background: #f2f2f2; padding: 0 2px; word-break: break-word; }
blockquote { margin: 4pt 0; padding: 2pt 8pt; border-left: 3px solid #aaa; color: #444; }
pre.mermaid { text-align: center; page-break-inside: avoid; background: none; }
img { max-width: 100%; max-height: 120mm; display: block; margin: 4pt auto; border: 1px solid #ccc; }
.completar { background: #fff3a0; }
"""

PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><base href="{base}"><title>{titulo}</title>
<style>{estilo}</style></head><body>{cuerpo}
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
  if (window.mermaid) {{
    mermaid.initialize({{ startOnLoad: false, theme: "neutral", securityLevel: "loose" }});
    mermaid.run({{ querySelector: "pre.mermaid" }});
  }}
</script></body></html>"""


def a_html(texto: str, titulo: str) -> str:
    # Los bloques mermaid se pasan tal cual para que mermaid.js los dibuje.
    bloques: list[str] = []

    def guardar(m: re.Match) -> str:
        bloques.append(m.group(1))
        return f"\n\nMERMAID{len(bloques) - 1}FIN\n\n"

    texto = re.sub(r"```mermaid\n(.*?)```", guardar, texto, flags=re.S)
    cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])
    for i, bloque in enumerate(bloques):
        cuerpo = cuerpo.replace(f"<p>MERMAID{i}FIN</p>", f'<pre class="mermaid">{html.escape(bloque)}</pre>')
    cuerpo = re.sub(r"(\[COMPLETAR[^\]]*\])", r'<span class="completar">\1</span>', cuerpo)
    return PLANTILLA.format(titulo=html.escape(titulo), estilo=ESTILO, cuerpo=cuerpo, base=DOCS.as_uri() + "/")


def buscar_navegador() -> str | None:
    for candidato in NAVEGADORES:
        if Path(candidato).exists() or shutil.which(candidato):
            return candidato
    return None


def contar_paginas(pdf: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?!s)", pdf.read_bytes()))


def main() -> int:
    navegador = buscar_navegador()
    if navegador is None:
        print("No se encontró Chrome ni Edge. Exporte los .md desde Word o Google Docs.")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        for nombre in DOCUMENTOS:
            fuente = DOCS / f"{nombre}.md"
            pagina = Path(tmp) / f"{nombre}.html"
            pagina.write_text(a_html(fuente.read_text(encoding="utf-8"), nombre), encoding="utf-8")
            destino = DOCS / f"{nombre}.pdf"
            subprocess.run([navegador, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--virtual-time-budget=15000", f"--user-data-dir={Path(tmp) / 'perfil'}",
                            f"--print-to-pdf={destino}", pagina.as_uri()],
                           capture_output=True, timeout=120)
            if not destino.exists():
                print(f"No se pudo generar {destino.name}.")
                return 1
            print(f"{destino.relative_to(RAIZ).as_posix()}: {contar_paginas(destino)} página(s)")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
