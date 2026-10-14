"""Ejecuta `python -m pytest -v` y guarda la salida en evidencias/resultados_pruebas.txt.

Uso:  python scripts/ejecutar_pruebas.py
La cabecera registra fecha, versión de Python y de pytest. Devuelve el código de salida de pytest.
"""
from __future__ import annotations

import datetime as dt
import os
import platform
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "evidencias" / "resultados_pruebas.txt"


def main() -> int:
    import pytest

    entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
    proceso = subprocess.run([sys.executable, "-m", "pytest", "-v", "-p", "no:cacheprovider"], cwd=RAIZ,
                             capture_output=True, text=True, encoding="utf-8", errors="replace", env=entorno)
    cabecera = (
        "Registro de la última ejecución de pruebas automatizadas\n"
        f"Fecha: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}\n"
        f"Python: {platform.python_version()} ({platform.system()} {platform.release()})\n"
        f"pytest: {pytest.__version__}\n"
        "Comando: python -m pytest -v\n"
        f"Código de salida: {proceso.returncode}\n"
        + "=" * 78 + "\n"
    )
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(cabecera + proceso.stdout + proceso.stderr, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(proceso.stdout.strip().splitlines()[-1])
    print(f"Guardado en {SALIDA.relative_to(RAIZ).as_posix()}")
    return proceso.returncode


if __name__ == "__main__":
    sys.exit(main())
