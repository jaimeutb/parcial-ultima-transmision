"""Validación del contenido de una historia (N06).

`validar` recorre el diccionario completo y devuelve TODOS los errores
encontrados; `construir_historia` solo crea el modelo si no hay ninguno.
El validador no conoce ninguna historia concreta: solo aplica el contrato.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from motor.modelo import Escena, Historia, Opcion

ARCHIVO_ILEGIBLE = "ARCHIVO_ILEGIBLE"
ESTRUCTURA_INVALIDA = "ESTRUCTURA_INVALIDA"
CAMPO_FALTANTE = "CAMPO_FALTANTE"
INICIO_INEXISTENTE = "INICIO_INEXISTENTE"
ESCENA_DUPLICADA = "ESCENA_DUPLICADA"
OPCION_DUPLICADA = "OPCION_DUPLICADA"
DESTINO_INEXISTENTE = "DESTINO_INEXISTENTE"
VARIABLE_NO_DECLARADA = "VARIABLE_NO_DECLARADA"
VALOR_NO_BOOLEANO = "VALOR_NO_BOOLEANO"
OPCIONES_INCOMPATIBLES_CON_FINAL = "OPCIONES_INCOMPATIBLES_CON_FINAL"

CODIGOS_ERROR = (
    ARCHIVO_ILEGIBLE,
    ESTRUCTURA_INVALIDA,
    CAMPO_FALTANTE,
    INICIO_INEXISTENTE,
    ESCENA_DUPLICADA,
    OPCION_DUPLICADA,
    DESTINO_INEXISTENTE,
    VARIABLE_NO_DECLARADA,
    VALOR_NO_BOOLEANO,
    OPCIONES_INCOMPATIBLES_CON_FINAL,
)

CAMPOS_HISTORIA = (("titulo", str), ("inicio", str), ("variables", dict), ("escenas", list))
CAMPOS_ESCENA = (("id", str), ("texto", str), ("final", bool), ("opciones", list))
CAMPOS_OPCION = (("id", str), ("texto", str), ("destino", str), ("condiciones", dict), ("efectos", dict))

_NOMBRE_TIPO = {str: "un texto", bool: "un booleano (true/false)", dict: "un objeto {…}", list: "una lista […]"}


@dataclass(frozen=True)
class ErrorContenido:
    codigo: str
    mensaje: str
    ubicacion: str

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.ubicacion}: {self.mensaje}"


class HistoriaInvalida(Exception):
    """La historia no puede jugarse; `errores` contiene todos los problemas detectados."""

    def __init__(self, errores: list[ErrorContenido]):
        super().__init__(f"La historia contiene {len(errores)} error(es).")
        self.errores = list(errores)


def _describir(valor: Any) -> str:
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, str):
        return f'"{valor}"'
    if valor is None:
        return "null"
    if isinstance(valor, (dict, list)):
        return "un objeto" if isinstance(valor, dict) else "una lista"
    return str(valor)


def _contexto(id_escena: Any = None, id_opcion: Any = None) -> str:
    partes = []
    if isinstance(id_escena, str):
        partes.append(f"escena '{id_escena}'")
    if isinstance(id_opcion, str):
        partes.append(f"opción '{id_opcion}'")
    return f" ({', '.join(partes)})" if partes else ""


class _Validador:
    def __init__(self, datos: Any):
        self.datos = datos
        self.errores: list[ErrorContenido] = []

    def error(self, codigo: str, mensaje: str, ubicacion: str) -> None:
        self.errores.append(ErrorContenido(codigo, mensaje, ubicacion))

    def campos(self, objeto: dict, esquema, ruta: str, que: str, contexto: str = "") -> dict:
        """Comprueba presencia y tipo de cada campo; devuelve solo los campos válidos."""
        validos = {}
        for nombre, tipo in esquema:
            ubicacion = f"{ruta}{nombre}{contexto}"
            if nombre not in objeto:
                self.error(CAMPO_FALTANTE, f"Falta el campo obligatorio '{nombre}' en {que}.", ubicacion)
            elif not isinstance(objeto[nombre], tipo):
                self.error(
                    ESTRUCTURA_INVALIDA,
                    f"El campo '{nombre}' de {que} debe ser {_NOMBRE_TIPO[tipo]}, "
                    f"pero contiene {_describir(objeto[nombre])}.",
                    ubicacion,
                )
            else:
                validos[nombre] = objeto[nombre]
        return validos

    def ejecutar(self) -> list[ErrorContenido]:
        if not isinstance(self.datos, dict):
            self.error(
                ESTRUCTURA_INVALIDA,
                f"La raíz del archivo debe ser un objeto {{…}} con la historia, pero es {_describir(self.datos)}.",
                "(raíz)",
            )
            return self.errores

        historia = self.campos(self.datos, CAMPOS_HISTORIA, "", "la historia")
        variables = historia.get("variables")
        if variables is not None:
            for nombre, valor in variables.items():
                if not isinstance(valor, bool):
                    self.error(
                        VALOR_NO_BOOLEANO,
                        f"La variable '{nombre}' debe tener un valor inicial true o false, "
                        f"pero tiene {_describir(valor)}.",
                        f"variables.{nombre}",
                    )

        escenas = historia.get("escenas")
        if escenas is None:
            return self.errores
        if not escenas:
            self.error(ESTRUCTURA_INVALIDA, "La lista 'escenas' está vacía; la historia necesita al menos una escena.", "escenas")

        ids_escenas = self.recolectar_ids_escenas(escenas)
        for i, escena in enumerate(escenas):
            self.validar_escena(escena, f"escenas[{i}]", ids_escenas, variables)

        inicio = historia.get("inicio")
        if inicio is not None and inicio not in ids_escenas:
            self.error(
                INICIO_INEXISTENTE,
                f"La escena inicial '{inicio}' no existe entre las escenas de la historia.",
                "inicio",
            )
        return self.errores

    def recolectar_ids_escenas(self, escenas: list) -> set[str]:
        vistos: set[str] = set()
        for i, escena in enumerate(escenas):
            id_escena = escena.get("id") if isinstance(escena, dict) else None
            if not isinstance(id_escena, str):
                continue
            if id_escena in vistos:
                self.error(
                    ESCENA_DUPLICADA,
                    f"El ID de escena '{id_escena}' está repetido; cada escena necesita un ID único.",
                    f"escenas[{i}].id{_contexto(id_escena)}",
                )
            vistos.add(id_escena)
        return vistos

    def validar_escena(self, escena: Any, ruta: str, ids_escenas: set[str], variables: dict | None) -> None:
        if not isinstance(escena, dict):
            self.error(ESTRUCTURA_INVALIDA, f"Cada escena debe ser un objeto {{…}}, pero se encontró {_describir(escena)}.", ruta)
            return
        id_escena = escena.get("id")
        campos = self.campos(escena, CAMPOS_ESCENA, f"{ruta}.", "la escena", _contexto(id_escena))
        opciones = campos.get("opciones")
        if opciones is None:
            return

        final = campos.get("final")
        if final is True and opciones:
            self.error(
                OPCIONES_INCOMPATIBLES_CON_FINAL,
                f"La escena final '{id_escena}' tiene {len(opciones)} opción(es); una escena final debe tener cero opciones.",
                f"{ruta}.opciones{_contexto(id_escena)}",
            )
        elif final is False and not opciones:
            self.error(
                OPCIONES_INCOMPATIBLES_CON_FINAL,
                f"La escena '{id_escena}' no es final y no tiene opciones; necesita al menos una.",
                f"{ruta}.opciones{_contexto(id_escena)}",
            )

        ids_opciones: set[str] = set()
        for j, opcion in enumerate(opciones):
            self.validar_opcion(opcion, f"{ruta}.opciones[{j}]", id_escena, ids_opciones, ids_escenas, variables)

    def validar_opcion(self, opcion: Any, ruta: str, id_escena: Any, ids_opciones: set[str],
                       ids_escenas: set[str], variables: dict | None) -> None:
        if not isinstance(opcion, dict):
            self.error(
                ESTRUCTURA_INVALIDA,
                f"Cada opción debe ser un objeto {{…}}, pero se encontró {_describir(opcion)}.",
                f"{ruta}{_contexto(id_escena)}",
            )
            return
        id_opcion = opcion.get("id")
        contexto = _contexto(id_escena, id_opcion)
        campos = self.campos(opcion, CAMPOS_OPCION, f"{ruta}.", "la opción", contexto)

        if "id" in campos:
            if id_opcion in ids_opciones:
                self.error(
                    OPCION_DUPLICADA,
                    f"El ID de opción '{id_opcion}' está repetido dentro de la escena '{id_escena}'.",
                    f"{ruta}.id{contexto}",
                )
            ids_opciones.add(id_opcion)

        destino = campos.get("destino")
        if destino is not None and destino not in ids_escenas:
            self.error(
                DESTINO_INEXISTENTE,
                f"El destino '{destino}' no corresponde a ninguna escena de la historia.",
                f"{ruta}.destino{contexto}",
            )

        for mapa in ("condiciones", "efectos"):
            for nombre, valor in campos.get(mapa, {}).items():
                ubicacion = f"{ruta}.{mapa}.{nombre}{contexto}"
                if variables is not None and nombre not in variables:
                    self.error(
                        VARIABLE_NO_DECLARADA,
                        f"La variable '{nombre}' usada en '{mapa}' no está declarada en 'variables'.",
                        ubicacion,
                    )
                if not isinstance(valor, bool):
                    self.error(
                        VALOR_NO_BOOLEANO,
                        f"El valor de '{nombre}' en '{mapa}' debe ser true o false, pero es {_describir(valor)}.",
                        ubicacion,
                    )


def validar(datos: Any) -> list[ErrorContenido]:
    """Devuelve la lista completa de errores del contenido (vacía si es válido)."""
    return _Validador(datos).ejecutar()


def construir_historia(datos: Any) -> Historia:
    """Construye el modelo solo si hay 0 errores; si no, lanza HistoriaInvalida."""
    errores = validar(datos)
    if errores:
        raise HistoriaInvalida(errores)
    escenas = [
        Escena(
            id=e["id"],
            texto=e["texto"],
            final=e["final"],
            opciones=tuple(
                Opcion(o["id"], o["texto"], o["destino"], o["condiciones"], o["efectos"]) for o in e["opciones"]
            ),
        )
        for e in datos["escenas"]
    ]
    return Historia(datos["titulo"], datos["inicio"], datos["variables"], tuple(escenas))
