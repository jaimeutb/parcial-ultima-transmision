"""Construye el ZIP de entrega: Parcial_<ApellidoNombre>_<ApellidoNombre>.zip

Uso:
  python scripts/empaquetar.py --simular PerezLaura GomezAndres   # arma el ZIP en una carpeta temporal, lo revisa y lo borra
  python scripts/empaquetar.py PerezLaura GomezAndres             # regenera el historial Git y crea el ZIP en la raíz

Incluye código, historias, pruebas, scripts, docs (con PDFs), evidencias, README y entrega/video.mp4 si existe.
Excluye .git, .venv, __pycache__, .pytest_cache, *.pyc y enunciado/.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INCLUIR = ["motor", "historias", "tests", "scripts", "docs", "evidencias", "README.md", "requirements.txt",
           "pytest.ini", "entrega/video.mp4"]
CARPETAS_EXCLUIDAS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "enunciado"}
EXTENSIONES_EXCLUIDAS = {".pyc", ".pyo"}
NOMBRE_VALIDO = re.compile(r"^[A-Z][a-z]+[A-Z][a-z]+$")
HISTORIAL = RAIZ / "evidencias" / "historial_git.txt"


def validar_nombre(nombre: str) -> str | None:
    if not nombre.isascii() or not nombre.isalpha():
        return f"'{nombre}': use solo letras sin tildes, sin ñ y sin espacios (ApellidoNombre)."
    if not NOMBRE_VALIDO.match(nombre):
        return f"'{nombre}': el formato esperado es ApellidoNombre, p. ej. PerezLaura."
    return None


def archivos_a_incluir() -> list[Path]:
    archivos = []
    for entrada in INCLUIR:
        ruta = RAIZ / entrada
        candidatos = [ruta] if ruta.is_file() else sorted(ruta.rglob("*")) if ruta.is_dir() else []
        for archivo in candidatos:
            relativa = archivo.relative_to(RAIZ)
            if (archivo.is_file() and not CARPETAS_EXCLUIDAS.intersection(relativa.parts)
                    and archivo.suffix not in EXTENSIONES_EXCLUIDAS):
                archivos.append(archivo)
    return archivos


def regenerar_historial() -> bool:
    try:
        salida = subprocess.run(
            ["git", "log", "--all", "--decorate", "--date=iso", "--pretty=format:%h | %an <%ae> | %ad | %d %s"],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return False
    HISTORIAL.write_text(salida + "\n", encoding="utf-8")
    return True


def historial_al_dia() -> bool:
    try:
        cabeza = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                                text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return HISTORIAL.exists()
    return HISTORIAL.exists() and HISTORIAL.read_text(encoding="utf-8").startswith(cabeza)


def advertencias(nombres: set[str], simular: bool) -> list[str]:
    avisos = []
    for requerido in ["docs/informe.pdf", "docs/anexo.pdf", "evidencias/resultados_pruebas.txt",
                      "evidencias/rnf/resultado_rnf.txt"]:
        if requerido not in nombres:
            avisos.append(f"Falta {requerido}.")
    if "evidencias/historial_git.txt" not in nombres:
        avisos.append("Falta evidencias/historial_git.txt.")
    elif simular and not historial_al_dia():
        avisos.append("evidencias/historial_git.txt no incluye el último commit (se regenera al empaquetar de verdad).")
    capturas = [n for n in nombres if n.startswith("evidencias/tablero/") and n.lower().endswith((".png", ".jpg", ".jpeg"))]
    if len(capturas) < 2:
        avisos.append(f"Se esperan al menos 2 capturas del tablero en evidencias/tablero/ (hay {len(capturas)}).")
    readme = (RAIZ / "README.md").read_text(encoding="utf-8") if (RAIZ / "README.md").exists() else ""
    seccion_video = readme.split("## Demostración en video", 1)[-1].split("\n## ", 1)[0]
    if "entrega/video.mp4" not in nombres and ("[COMPLETAR" in seccion_video or "http" not in seccion_video):
        avisos.append("No hay entrega/video.mp4 ni un enlace al video en el README.")
    pendientes = []
    for archivo in [RAIZ / "README.md", *sorted((RAIZ / "docs").glob("*.md"))]:
        if archivo.exists():
            cantidad = archivo.read_text(encoding="utf-8").count("[COMPLETAR")
            if cantidad:
                pendientes.append(f"{archivo.relative_to(RAIZ).as_posix()} ({cantidad})")
    if pendientes:
        avisos.append("Quedan [COMPLETAR] en: " + ", ".join(pendientes))
    return avisos


def construir_zip(destino: Path, carpeta: str, archivos: list[Path]) -> None:
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED) as zip_:
        for archivo in archivos:
            zip_.write(archivo, f"{carpeta}/{archivo.relative_to(RAIZ).as_posix()}")


def revisar_zip(ruta: Path, carpeta: str) -> set[str]:
    """Reabre el ZIP, comprueba su integridad, lo extrae en una carpeta temporal y devuelve sus rutas."""
    with zipfile.ZipFile(ruta) as zip_:
        danado = zip_.testzip()
        if danado:
            raise RuntimeError(f"El ZIP está dañado en {danado}")
        with tempfile.TemporaryDirectory() as tmp:
            zip_.extractall(tmp)
            extraidos = {p.relative_to(Path(tmp) / carpeta).as_posix() for p in Path(tmp).rglob("*") if p.is_file()}
    return extraidos


def main(argumentos: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    simular = "--simular" in argumentos
    nombres = [a for a in argumentos if a != "--simular"]
    if len(nombres) != 2:
        print(__doc__)
        return 2
    errores = [e for e in map(validar_nombre, nombres) if e]
    if errores:
        print("\n".join(errores))
        return 2

    carpeta = f"Parcial_{nombres[0]}_{nombres[1]}"
    if not simular and not regenerar_historial():
        print("Aviso: no se pudo regenerar evidencias/historial_git.txt (¿Git disponible?).")
    archivos = archivos_a_incluir()

    with tempfile.TemporaryDirectory() as tmp:
        destino = (Path(tmp) if simular else RAIZ) / f"{carpeta}.zip"
        construir_zip(destino, carpeta, archivos)
        contenido = revisar_zip(destino, carpeta)
        tamano = destino.stat().st_size

    print(f"{'SIMULACIÓN — ' if simular else ''}{carpeta}.zip: {len(contenido)} archivos, {tamano / 1024:.0f} KB; "
          "se extrae correctamente.")
    for nombre in sorted(contenido):
        print(f"  {nombre}")
    avisos = advertencias(contenido, simular)
    print()
    if avisos:
        print("Advertencias:")
        for aviso in avisos:
            print(f"  - {aviso}")
    else:
        print("Sin advertencias.")
    print("\nNo se creó ningún archivo (simulación)." if simular else f"\nCreado: {carpeta}.zip")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
