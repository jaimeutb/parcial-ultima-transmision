"""Lectura de archivos de historia (N01).

Convierte un archivo JSON en un diccionario y traduce cualquier problema de
lectura en un ErrorContenido con código ARCHIVO_ILEGIBLE.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from motor.modelo import Historia
from motor.validador import ARCHIVO_ILEGIBLE, ErrorContenido, HistoriaInvalida, construir_historia


_SINTAXIS = {
    "Expecting value": "se esperaba un valor",
    "Expecting ',' delimiter": "falta una coma ','",
    "Expecting ':' delimiter": "faltan los dos puntos ':'",
    "Expecting property name enclosed in double quotes": "los nombres de campo deben ir entre comillas dobles",
    "Unterminated string starting at": "hay un texto sin comillas de cierre",
    "Extra data": "hay contenido después del final del objeto principal",
}


def _ilegible(ruta: Path, mensaje: str) -> HistoriaInvalida:
    return HistoriaInvalida([ErrorContenido(ARCHIVO_ILEGIBLE, mensaje, str(ruta))])


def leer_archivo(ruta: str | Path) -> Any:
    """Lee el archivo y devuelve el contenido JSON; lanza HistoriaInvalida si no es posible."""
    ruta = Path(ruta)
    if ruta.is_dir():
        raise _ilegible(ruta, f"'{ruta}' es una carpeta, no un archivo de historia.")
    try:
        # utf-8-sig acepta archivos guardados con BOM por editores de Windows.
        with ruta.open(encoding="utf-8-sig") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        raise _ilegible(ruta, f"No se encontró el archivo '{ruta}'.") from None
    except PermissionError:
        raise _ilegible(ruta, f"No hay permiso para leer el archivo '{ruta}'.") from None
    except UnicodeDecodeError:
        raise _ilegible(ruta, f"El archivo '{ruta}' no está guardado con codificación UTF-8.") from None
    except json.JSONDecodeError as e:
        causa = _SINTAXIS.get(e.msg, "error de sintaxis")
        raise _ilegible(
            ruta, f"El archivo '{ruta.name}' no contiene JSON válido: {causa} (línea {e.lineno}, columna {e.colno})."
        ) from None
    except (OSError, ValueError, RecursionError) as e:
        raise _ilegible(ruta, f"No se pudo leer el archivo '{ruta}': {e.__class__.__name__}.") from None


def cargar_historia(ruta: str | Path) -> Historia:
    """Lee y valida la historia completa antes de permitir cualquier partida."""
    return construir_historia(leer_archivo(ruta))
