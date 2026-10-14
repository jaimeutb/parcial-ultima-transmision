"""Reglas de una partida (N02–N05). Sin entrada/salida: la CLI es solo un adaptador.

La sesión nunca modifica la Historia ni sus variables iniciales: trabaja
siempre sobre copias y solo confirma el nuevo estado cuando la elección
superó todas las validaciones.
"""
from __future__ import annotations

from dataclasses import dataclass

from motor.modelo import Escena, Historia, Opcion

OK = "OK"
OPCION_INEXISTENTE = "OPCION_INEXISTENTE"
OPCION_NO_HABILITADA = "OPCION_NO_HABILITADA"
PARTIDA_FINALIZADA = "PARTIDA_FINALIZADA"


@dataclass(frozen=True)
class ResultadoAccion:
    codigo: str
    mensaje: str

    @property
    def ok(self) -> bool:
        return self.codigo == OK


class Sesion:
    def __init__(self, historia: Historia):
        self._historia = historia
        self._id_escena = historia.inicio
        self._variables = dict(historia.variables)

    @property
    def historia(self) -> Historia:
        return self._historia

    @property
    def escena_actual(self) -> Escena:
        return self._historia.escena(self._id_escena)

    @property
    def variables(self) -> dict[str, bool]:
        """Copia del estado: modificarla no altera la partida."""
        return dict(self._variables)

    @property
    def es_final(self) -> bool:
        return self.escena_actual.final

    @property
    def esta_bloqueada(self) -> bool:
        """Escena no final sin ninguna opción habilitada con el estado actual."""
        return not self.es_final and not self.opciones_habilitadas()

    def opciones_habilitadas(self) -> list[Opcion]:
        return [o for o in self.escena_actual.opciones if o.esta_habilitada(self._variables)]

    def elegir(self, id_opcion: str) -> ResultadoAccion:
        if self.es_final:
            return ResultadoAccion(PARTIDA_FINALIZADA, "La partida terminó. Reinicie para jugar de nuevo.")
        opcion = self.escena_actual.buscar_opcion(id_opcion)
        if opcion is None:
            return ResultadoAccion(OPCION_INEXISTENTE, f"La opción '{id_opcion}' no existe en esta escena.")
        if not opcion.esta_habilitada(self._variables):
            return ResultadoAccion(
                OPCION_NO_HABILITADA, f"La opción '{id_opcion}' no está disponible con la información actual."
            )
        nuevas = dict(self._variables)
        nuevas.update(opcion.efectos)
        # Escena y variables se confirman juntas, después de validar la elección.
        self._id_escena = opcion.destino
        self._variables = nuevas
        return ResultadoAccion(OK, f"Elegiste: {opcion.texto}.")

    def reiniciar(self) -> None:
        self._id_escena = self._historia.inicio
        self._variables = dict(self._historia.variables)
