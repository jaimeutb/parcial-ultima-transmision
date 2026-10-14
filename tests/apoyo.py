"""Utilidades compartidas por las pruebas y por scripts/verificar_rnf.py."""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

from motor.modelo import Historia
from motor.sesion import Sesion
from motor.validador import construir_historia

RAIZ = Path(__file__).resolve().parent.parent
RUTA_OFICIAL = RAIZ / "historias" / "la_ultima_transmision.json"
RUTA_FARO = RAIZ / "historias" / "el_faro.json"
RUTA_DESTINO_INEXISTENTE = RAIZ / "historias" / "invalidas" / "destino_inexistente.json"


@lru_cache(maxsize=None)
def _leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8")


def datos_de(ruta: Path) -> dict:
    """Copia profunda e independiente del contenido JSON de una historia."""
    return copy.deepcopy(json.loads(_leer(ruta)))


def datos_oficiales() -> dict:
    return datos_de(RUTA_OFICIAL)


def sesion_oficial() -> Sesion:
    return Sesion(construir_historia(datos_oficiales()))


def ids(opciones) -> list[str]:
    return [o.id for o in opciones]


def estado(sesion: Sesion) -> tuple[str, dict[str, bool]]:
    return sesion.escena_actual.id, sesion.variables


def escena(datos: dict, id_escena: str) -> dict:
    return next(e for e in datos["escenas"] if e["id"] == id_escena)


def opcion(datos: dict, id_escena: str, id_opcion: str) -> dict:
    return next(o for o in escena(datos, id_escena)["opciones"] if o["id"] == id_opcion)


def nueva_opcion(id_opcion: str, destino: str, condiciones=None, efectos=None) -> dict:
    return {"id": id_opcion, "texto": f"Opción {id_opcion}", "destino": destino,
            "condiciones": condiciones or {}, "efectos": efectos or {}}


def nueva_escena(id_escena: str, opciones: list[dict] | None = None) -> dict:
    opciones = opciones or []
    return {"id": id_escena, "texto": f"Texto de {id_escena}", "final": not opciones, "opciones": opciones}


def historia_en_memoria(variables: dict, escenas: list[dict], inicio: str | None = None) -> Historia:
    datos = {"titulo": "Prueba", "inicio": inicio or escenas[0]["id"], "variables": variables, "escenas": escenas}
    return construir_historia(datos)


def escribir_json(directorio: Path, nombre: str, contenido) -> Path:
    ruta = directorio / nombre
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


# ---------------------------------------------------------------------------
# Casos de contenido inválido: uno o más por cada código de error (U4, RNF-02)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CasoInvalido:
    nombre: str
    codigo: str
    preparar: Callable[[Path], Path]   # recibe una carpeta temporal y devuelve la ruta a validar
    fragmentos: tuple[str, ...]        # ID o campo que el diagnóstico debe mencionar


def _mutar(nombre: str, cambio: Callable[[dict], None]) -> Callable[[Path], Path]:
    def preparar(directorio: Path) -> Path:
        datos = datos_oficiales()
        cambio(datos)
        return escribir_json(directorio, f"{nombre}.json", datos)
    return preparar


def _texto(nombre: str, contenido: bytes) -> Callable[[Path], Path]:
    def preparar(directorio: Path) -> Path:
        ruta = directorio / f"{nombre}.json"
        ruta.write_bytes(contenido)
        return ruta
    return preparar


def _caso(nombre: str, codigo: str, cambio: Callable[[dict], None], *fragmentos: str) -> CasoInvalido:
    return CasoInvalido(nombre, codigo, _mutar(nombre, cambio), fragmentos)


def _asignar(destino: dict, clave: str, valor) -> None:
    destino[clave] = valor


CASOS_INVALIDOS: list[CasoInvalido] = [
    CasoInvalido("ilegible_inexistente", "ARCHIVO_ILEGIBLE",
                 lambda d: d / "no_existe.json", ("no_existe.json",)),
    CasoInvalido("ilegible_json_roto", "ARCHIVO_ILEGIBLE",
                 _texto("ilegible_json_roto", b'{"titulo": "Roto", "inicio": '), ("ilegible_json_roto.json", "línea")),
    CasoInvalido("ilegible_no_utf8", "ARCHIVO_ILEGIBLE",
                 _texto("ilegible_no_utf8", b'{"titulo": "\xff\xfe"}'), ("ilegible_no_utf8.json", "UTF-8")),
    CasoInvalido("estructura_raiz_lista", "ESTRUCTURA_INVALIDA",
                 _texto("estructura_raiz_lista", b"[]"), ("(raíz)",)),
    _caso("estructura_escenas_no_lista", "ESTRUCTURA_INVALIDA",
          lambda d: _asignar(d, "escenas", "E1"), "escenas"),
    _caso("estructura_condiciones_no_objeto", "ESTRUCTURA_INVALIDA",
          lambda d: _asignar(opcion(d, "E3", "activar_codigo"), "condiciones", ["conoce_origen"]),
          "condiciones", "activar_codigo"),
    _caso("estructura_final_no_booleano", "ESTRUCTURA_INVALIDA",
          lambda d: _asignar(escena(d, "E4"), "final", "si"), "final", "E4"),
    _caso("campo_faltante_titulo", "CAMPO_FALTANTE", lambda d: d.pop("titulo"), "titulo"),
    _caso("campo_faltante_texto_escena", "CAMPO_FALTANTE", lambda d: escena(d, "E2").pop("texto"), "texto", "E2"),
    _caso("campo_faltante_destino", "CAMPO_FALTANTE",
          lambda d: opcion(d, "E2", "investigar").pop("destino"), "destino", "investigar"),
    _caso("inicio_inexistente", "INICIO_INEXISTENTE", lambda d: _asignar(d, "inicio", "E0"), "E0"),
    _caso("escena_duplicada", "ESCENA_DUPLICADA", lambda d: _asignar(escena(d, "E5"), "id", "E4"), "E4"),
    _caso("opcion_duplicada", "OPCION_DUPLICADA",
          lambda d: _asignar(opcion(d, "E2", "continuar"), "id", "investigar"), "investigar", "E2"),
    CasoInvalido("destino_inexistente_CA03", "DESTINO_INEXISTENTE",
                 lambda d: RUTA_DESTINO_INEXISTENTE, ("E99", "investigar")),
    _caso("variable_no_declarada_condicion", "VARIABLE_NO_DECLARADA",
          lambda d: _asignar(opcion(d, "E3", "activar_codigo"), "condiciones", {"tiene_mapa": True}), "tiene_mapa"),
    _caso("variable_no_declarada_efecto", "VARIABLE_NO_DECLARADA",
          lambda d: _asignar(opcion(d, "E2", "investigar")["efectos"], "sabe_nombre", True), "sabe_nombre"),
    _caso("valor_no_booleano_variable", "VALOR_NO_BOOLEANO",
          lambda d: _asignar(d["variables"], "conoce_origen", 0), "conoce_origen"),
    _caso("valor_no_booleano_condicion", "VALOR_NO_BOOLEANO",
          lambda d: _asignar(opcion(d, "E3", "activar_codigo")["condiciones"], "conoce_origen", "true"),
          "conoce_origen", "activar_codigo"),
    _caso("valor_no_booleano_efecto", "VALOR_NO_BOOLEANO",
          lambda d: _asignar(opcion(d, "E2", "investigar")["efectos"], "conoce_origen", 1),
          "conoce_origen", "investigar"),
    _caso("final_con_opciones", "OPCIONES_INCOMPATIBLES_CON_FINAL",
          lambda d: _asignar(escena(d, "E4"), "opciones", [nueva_opcion("volver", "E1")]), "E4"),
    _caso("no_final_sin_opciones", "OPCIONES_INCOMPATIBLES_CON_FINAL",
          lambda d: _asignar(escena(d, "E1"), "opciones", []), "E1"),
]
