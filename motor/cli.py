"""Interfaz de consola: el único módulo con input/print.

Traduce lo que escribe el lector a llamadas de Sesion y muestra los
resultados. Ningún error llega al usuario como traceback.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from motor.cargador import cargar_historia
from motor.modelo import Historia
from motor.sesion import Sesion
from motor.validador import HistoriaInvalida

USO = """Uso:
  python -m motor                      elegir una historia de la carpeta 'historias'
  python -m motor <ruta.json>          jugar la historia indicada
  python -m motor --validar <ruta>     solo validar el archivo, sin jugar
  python -m motor --ayuda              mostrar este mensaje"""

COMANDOS = {
    "r": "reiniciar", "reiniciar": "reiniciar",
    "q": "salir", "salir": "salir",
    "?": "ayuda", "ayuda": "ayuda",
    "e": "estado", "estado": "estado",
}

AYUDA = """Comandos:
  <número> o <id>   elegir una de las opciones mostradas
  e, estado         ver las variables de la partida
  r, reiniciar      empezar la historia desde el inicio
  ?, ayuda          mostrar esta ayuda
  q, salir          terminar el programa"""

Entrada = Callable[[str], str]
Salida = Callable[[str], None]


def _booleano(valor: bool) -> str:
    return "verdadero" if valor else "falso"


class Consola:
    def __init__(self, sesion: Sesion, entrada: Entrada = input, salida: Salida = print):
        self.sesion = sesion
        self.entrada = entrada
        self.salida = salida

    def comandos_disponibles(self) -> str:
        return "r reiniciar, q salir"

    def mostrar_escena(self) -> None:
        escena = self.sesion.escena_actual
        self.salida("")
        self.salida(f"[{escena.id}]")
        self.salida(escena.texto)
        if self.sesion.es_final:
            self.salida("")
            self.salida("«FIN»")
            self.salida(f"Opciones: {self.comandos_disponibles()}.")
        elif self.sesion.esta_bloqueada:
            self.salida("")
            self.salida("No hay opciones disponibles en esta escena.")
            self.salida(f"Puede continuar con: {self.comandos_disponibles()}.")
        else:
            for numero, opcion in enumerate(self.sesion.opciones_habilitadas(), start=1):
                self.salida(f"  {numero}) {opcion.texto}  [{opcion.id}]")

    def mostrar_estado(self) -> None:
        for nombre, valor in self.sesion.variables.items():
            self.salida(f"  {nombre} = {_booleano(valor)}")

    def ejecutar_comando(self, comando: str) -> tuple[bool, bool]:
        """Devuelve (seguir_jugando, volver_a_mostrar_la_escena)."""
        if comando == "salir":
            return False, False
        if comando == "reiniciar":
            self.sesion.reiniciar()
            self.salida("Partida reiniciada.")
            return True, True
        if comando == "estado":
            self.mostrar_estado()
            return True, False
        self.salida(AYUDA)
        return True, False

    def procesar(self, linea: str) -> tuple[bool, bool]:
        texto = linea.strip()
        if not texto:
            return True, False
        comando = COMANDOS.get(texto.lower())
        if comando:
            return self.ejecutar_comando(comando)
        id_opcion = texto
        if texto.isdigit():
            opciones = self.sesion.opciones_habilitadas()
            numero = int(texto)
            if not 1 <= numero <= len(opciones):
                self.salida(f"No hay una opción con el número {texto}. Escriba ? para ver los comandos.")
                return True, False
            id_opcion = opciones[numero - 1].id
        resultado = self.sesion.elegir(id_opcion)
        if not resultado.ok:
            self.salida(resultado.mensaje)
        return True, resultado.ok

    def ejecutar(self) -> int:
        titulo = self.sesion.historia.titulo
        self.salida(titulo)
        self.salida("=" * len(titulo))
        self.salida("Escriba el número o el id de una opción. ? muestra los comandos.")
        mostrar = True
        while True:
            if mostrar:
                self.mostrar_escena()
            try:
                linea = self.entrada("> ")
            except EOFError:
                self.salida("")
                self.salida("Fin de la entrada. Hasta pronto.")
                return 0
            seguir, mostrar = self.procesar(linea)
            if not seguir:
                self.salida("Hasta pronto.")
                return 0


def imprimir_errores(ruta: str, errores, salida: Salida = print) -> None:
    salida(f"La historia '{ruta}' no es válida ({len(errores)} error(es)). No se inicia ninguna partida.")
    for numero, error in enumerate(errores, start=1):
        salida(f"  {numero}. {error}")


def cargar_o_informar(ruta: str, salida: Salida = print) -> Historia | None:
    try:
        return cargar_historia(ruta)
    except HistoriaInvalida as e:
        imprimir_errores(ruta, e.errores, salida)
        return None


def elegir_historia(entrada: Entrada = input, salida: Salida = print) -> str | None:
    carpeta = Path("historias")
    disponibles = sorted(carpeta.glob("*.json")) if carpeta.is_dir() else []
    if not disponibles:
        salida("No se encontraron historias en la carpeta 'historias'.")
        salida(USO)
        return None
    salida("Historias disponibles:")
    for numero, ruta in enumerate(disponibles, start=1):
        salida(f"  {numero}) {ruta.as_posix()}")
    while True:
        texto = entrada("Elija un número (q para salir): ").strip().lower()
        if texto in ("q", "salir"):
            return None
        if texto.isdigit() and 1 <= int(texto) <= len(disponibles):
            return disponibles[int(texto) - 1].as_posix()
        salida("Número no válido.")


def _ejecutar(argumentos: list[str]) -> int:
    if argumentos and argumentos[0] in ("-h", "--help", "--ayuda"):
        print(USO)
        return 0
    if argumentos and argumentos[0] == "--validar":
        if len(argumentos) != 2:
            print("Indique un único archivo para validar.")
            print(USO)
            return 2
        historia = cargar_o_informar(argumentos[1])
        if historia is None:
            return 2
        print(f"Historia válida: «{historia.titulo}» ({len(historia.escenas)} escenas).")
        return 0
    if len(argumentos) > 1 or (argumentos and argumentos[0].startswith("-")):
        print(f"Argumentos no reconocidos: {' '.join(argumentos)}")
        print(USO)
        return 2

    ruta = argumentos[0] if argumentos else elegir_historia()
    if ruta is None:
        return 0
    historia = cargar_o_informar(ruta)
    if historia is None:
        return 2
    return Consola(Sesion(historia)).ejecutar()


def _configurar_salida() -> None:
    # UTF-8 en consola, tuberías y archivos; nunca falla por un carácter no representable.
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argumentos: list[str] | None = None) -> int:
    _configurar_salida()
    try:
        return _ejecutar(sys.argv[1:] if argumentos is None else argumentos)
    except KeyboardInterrupt:
        print("\nPartida interrumpida por el usuario. Hasta pronto.")
        return 130
    except Exception as e:  # Último recurso: nunca mostrar un traceback al lector.
        print(f"Error inesperado ({e.__class__.__name__}). La partida no puede continuar.")
        return 1
