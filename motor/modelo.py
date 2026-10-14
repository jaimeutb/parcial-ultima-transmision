"""Modelo de dominio inmutable: Historia, Escena y Opcion.

Las instancias solo se construyen desde el validador, cuando el contenido
no tiene errores. Los mapas se exponen como solo lectura para que ninguna
sesión pueda modificar la historia cargada.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


def _solo_lectura(mapa: Mapping[str, bool]) -> Mapping[str, bool]:
    return MappingProxyType(dict(mapa))


@dataclass(frozen=True)
class Opcion:
    id: str
    texto: str
    destino: str
    condiciones: Mapping[str, bool]
    efectos: Mapping[str, bool]

    def __post_init__(self) -> None:
        object.__setattr__(self, "condiciones", _solo_lectura(self.condiciones))
        object.__setattr__(self, "efectos", _solo_lectura(self.efectos))

    def esta_habilitada(self, variables: Mapping[str, bool]) -> bool:
        """Todas las condiciones deben cumplirse; un mapa vacío habilita la opción."""
        return all(variables.get(nombre) == valor for nombre, valor in self.condiciones.items())


@dataclass(frozen=True)
class Escena:
    id: str
    texto: str
    final: bool
    opciones: tuple[Opcion, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "opciones", tuple(self.opciones))

    def buscar_opcion(self, id_opcion: object) -> Opcion | None:
        return next((o for o in self.opciones if o.id == id_opcion), None)


@dataclass(frozen=True)
class Historia:
    titulo: str
    inicio: str
    variables: Mapping[str, bool]
    escenas: tuple[Escena, ...]
    _indice: Mapping[str, Escena] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "variables", _solo_lectura(self.variables))
        object.__setattr__(self, "escenas", tuple(self.escenas))
        object.__setattr__(self, "_indice", MappingProxyType({e.id: e for e in self.escenas}))

    def escena(self, id_escena: str) -> Escena:
        return self._indice[id_escena]

    def tiene_escena(self, id_escena: object) -> bool:
        return isinstance(id_escena, str) and id_escena in self._indice
