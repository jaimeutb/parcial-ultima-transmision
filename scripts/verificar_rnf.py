"""Verificación reproducible de los requisitos no funcionales.

Uso:  python scripts/verificar_rnf.py
Escribe evidencias/rnf/resultado_rnf.txt y termina con código 0 si los tres RNF se cumplen.
Las mismas funciones se usan desde tests/test_rnf.py.
"""
from __future__ import annotations

import datetime as dt
import os
import platform
import random
import re
import string
import subprocess
import sys
import tempfile
from collections import Counter, deque
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from motor.cargador import cargar_historia, leer_archivo  # noqa: E402
from motor.modelo import Historia  # noqa: E402
from motor.sesion import OK, Sesion  # noqa: E402
from motor.validador import CODIGOS_ERROR  # noqa: E402
from tests.apoyo import CASOS_INVALIDOS, RUTA_FARO, RUTA_OFICIAL  # noqa: E402

HISTORIAS = (RUTA_OFICIAL, RUTA_FARO)
SALIDA = RAIZ / "evidencias" / "rnf" / "resultado_rnf.txt"
SEMILLA = 20261015


# ------------------------------------------------------------------ RNF-01 --

def finales_alcanzables(historia: Historia) -> set[str]:
    """Explora todos los estados (escena, variables) alcanzables desde el inicio, usando solo la Sesion."""
    vistos = set()
    pendientes = deque([[]])
    finales = set()
    while pendientes:
        camino = pendientes.popleft()
        sesion = Sesion(historia)
        for paso in camino:
            sesion.elegir(paso)
        clave = (sesion.escena_actual.id, tuple(sorted(sesion.variables.items())))
        if clave in vistos:
            continue
        vistos.add(clave)
        if sesion.es_final:
            finales.add(sesion.escena_actual.id)
        for opcion in sesion.opciones_habilitadas():
            pendientes.append(camino + [opcion.id])
    return finales


def literales_de_historias_en_motor() -> list[str]:
    """Busca IDs de escenas/opciones como literales y nombres de variables como palabra completa en motor/*.py."""
    ids, variables = set(), set()
    for ruta in HISTORIAS:
        datos = leer_archivo(ruta)
        variables |= set(datos["variables"])
        for escena in datos["escenas"]:
            ids.add(escena["id"])
            ids |= {o["id"] for o in escena["opciones"]}
    hallazgos = []
    for archivo in sorted((RAIZ / "motor").glob("*.py")):
        codigo = archivo.read_text(encoding="utf-8")
        for id_ in sorted(ids):
            if re.search(rf"([\"']){re.escape(id_)}\1", codigo):
                hallazgos.append(f"{archivo.name}: literal '{id_}'")
        for nombre in sorted(variables):
            if re.search(rf"\b{re.escape(nombre)}\b", codigo):
                hallazgos.append(f"{archivo.name}: variable '{nombre}'")
    return hallazgos


def lineas_de_motor_cambiadas_al_agregar(ruta: Path) -> int | None:
    """Líneas de motor/ modificadas en los commits que agregaron o cambiaron la historia (None sin Git)."""
    try:
        relativa = ruta.relative_to(RAIZ).as_posix()
        commits = subprocess.run(["git", "log", "--format=%H", "--", relativa], cwd=RAIZ,
                                 capture_output=True, text=True, check=True).stdout.split()
        total = 0
        for commit in commits:
            stat = subprocess.run(["git", "show", "--numstat", "--format=", commit, "--", "motor/"], cwd=RAIZ,
                                  capture_output=True, text=True, check=True).stdout
            for linea in stat.splitlines():
                agregadas, borradas, _ = linea.split("\t", 2)
                total += int(agregadas) + int(borradas)
        return total if commits else None
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None


def rnf01() -> dict:
    faro = cargar_historia(RUTA_FARO)
    declarados = {e.id for e in faro.escenas if e.final}
    opciones = [o for e in faro.escenas for o in e.opciones]
    return {
        "escenas": len(faro.escenas),
        "condiciones": sum(len(o.condiciones) for o in opciones),
        "efectos": sum(len(o.efectos) for o in opciones),
        "finales_declarados": sorted(declarados),
        "finales_alcanzados": sorted(finales_alcanzables(faro)),
        "finales_oficial": sorted(finales_alcanzables(cargar_historia(RUTA_OFICIAL))),
        "literales_en_motor": literales_de_historias_en_motor(),
        "lineas_motor_cambiadas": lineas_de_motor_cambiadas_al_agregar(RUTA_FARO),
    }


def rnf01_cumple(r: dict) -> bool:
    return (r["escenas"] >= 3 and r["condiciones"] >= 1 and r["efectos"] >= 1
            and r["finales_alcanzados"] == r["finales_declarados"]
            and r["finales_oficial"] == ["E4", "E5", "E6"]
            and not r["literales_en_motor"] and r["lineas_motor_cambiadas"] in (0, None))


# ------------------------------------------------------------------ RNF-02 --

def ejecutar_motor(*argumentos: str, entrada: str = "") -> subprocess.CompletedProcess:
    entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-m", "motor", *argumentos], cwd=RAIZ, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=entorno, timeout=30, input=entrada)


def evaluar_caso_invalido(caso, directorio: Path) -> dict:
    proceso = ejecutar_motor("--validar", str(caso.preparar(directorio)))
    # La carpeta temporal se abrevia para no publicar rutas locales en la evidencia.
    salida = (proceso.stdout + proceso.stderr).replace(str(directorio), "<tmp>").replace(str(RAIZ) + os.sep, "")
    return {
        "caso": caso.nombre,
        "codigo": caso.codigo,
        "salida_2": proceso.returncode == 2,
        "codigo_presente": f"[{caso.codigo}]" in salida,
        "id_o_campo_presente": all(f in salida for f in caso.fragmentos),
        "sin_traceback": "Traceback" not in salida,
        "mensaje": next((l.strip() for l in salida.splitlines() if f"[{caso.codigo}]" in l), salida.strip()[:200]),
    }


def rnf02() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        casos = [evaluar_caso_invalido(c, Path(tmp)) for c in CASOS_INVALIDOS]
    correcto = lambda c: c["salida_2"] and c["codigo_presente"] and c["id_o_campo_presente"] and c["sin_traceback"]
    cubiertos = {c["codigo"] for c in casos if correcto(c)}
    return {
        "casos": casos,
        "casos_correctos": sum(correcto(c) for c in casos),
        "codigos_cubiertos": len(cubiertos),
        "codigos_totales": len(CODIGOS_ERROR),
        "tracebacks": sum(not c["sin_traceback"] for c in casos),
    }


def rnf02_cumple(r: dict) -> bool:
    return r["codigos_cubiertos"] == r["codigos_totales"] and r["casos_correctos"] == len(r["casos"]) and r["tracebacks"] == 0


# ------------------------------------------------------------------ RNF-03 --

def invariantes(sesion: Sesion) -> list[str]:
    historia = sesion.historia
    fallos = []
    if not historia.tiene_escena(sesion.escena_actual.id):
        fallos.append("escena actual inexistente")
    variables = sesion.variables
    if set(variables) != set(historia.variables):
        fallos.append("claves de variables distintas de las declaradas")
    if not all(isinstance(v, bool) for v in variables.values()):
        fallos.append("variable no booleana")
    if sesion.es_final and sesion.opciones_habilitadas():
        fallos.append("final con opciones habilitadas")
    return fallos


def secuencias_aleatorias(historia: Historia, secuencias: int = 1000, acciones: int = 50, semilla: int = SEMILLA) -> dict:
    todas = sorted({o.id for e in historia.escenas for o in e.opciones})
    excepciones, violaciones, ejecutadas = 0, 0, 0
    tipos, codigos = Counter(), Counter()
    for n in range(secuencias):
        azar = random.Random(semilla + n)
        sesion = Sesion(historia)
        for _ in range(acciones):
            tipo = azar.choice(["valida", "id_cualquiera", "texto_aleatorio", "deshacer", "reiniciar"])
            antes = (sesion.escena_actual.id, sesion.variables)
            try:
                if tipo == "valida":
                    habilitadas = sesion.opciones_habilitadas()
                    resultado = sesion.elegir(azar.choice(habilitadas).id if habilitadas else "")
                elif tipo == "id_cualquiera":
                    resultado = sesion.elegir(azar.choice(todas))
                elif tipo == "texto_aleatorio":
                    largo = azar.randint(0, 12)
                    resultado = sesion.elegir("".join(azar.choice(string.printable) for _ in range(largo)))
                elif tipo == "deshacer":
                    resultado = sesion.deshacer()
                else:
                    sesion.reiniciar()
                    resultado = None
            except Exception:  # cualquier excepción no controlada cuenta como fallo
                excepciones += 1
                continue
            ejecutadas += 1
            tipos[tipo] += 1
            if resultado is not None:
                codigos[resultado.codigo] += 1
                if resultado.codigo != OK and (sesion.escena_actual.id, sesion.variables) != antes:
                    violaciones += 1  # una acción rechazada no debe cambiar el estado
            violaciones += bool(invariantes(sesion))
    return {
        "historia": historia.titulo, "secuencias": secuencias, "acciones_por_secuencia": acciones,
        "acciones_ejecutadas": ejecutadas, "excepciones": excepciones, "violaciones": violaciones,
        "tipos": dict(sorted(tipos.items())), "codigos": dict(sorted(codigos.items())),
    }


def rnf03(secuencias: int = 1000, acciones: int = 50) -> list[dict]:
    return [secuencias_aleatorias(cargar_historia(r), secuencias, acciones) for r in HISTORIAS]


def rnf03_cumple(resultados: list[dict]) -> bool:
    return all(r["excepciones"] == 0 and r["violaciones"] == 0
               and r["acciones_ejecutadas"] == r["secuencias"] * r["acciones_por_secuencia"] for r in resultados)


# ------------------------------------------------------------------ informe --

def _veredicto(ok: bool) -> str:
    return "CUMPLE" if ok else "NO CUMPLE"


def generar_informe() -> tuple[str, bool]:
    r1, r2, r3 = rnf01(), rnf02(), rnf03()
    ok1, ok2, ok3 = rnf01_cumple(r1), rnf02_cumple(r2), rnf03_cumple(r3)
    l = [
        "Verificación de requisitos no funcionales",
        f"Fecha: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Python: {platform.python_version()} ({platform.system()} {platform.release()})",
        f"Comando: python scripts/verificar_rnf.py   Semilla RNF-03: {SEMILLA}",
        "",
        f"RNF-01 Modificabilidad del contenido: {_veredicto(ok1)}",
        "  Meta: una historia nueva (>= 3 escenas, >= 1 condición, >= 1 efecto) se juega hasta todos sus finales "
        "con 0 líneas cambiadas en motor/.",
        f"  el_faro.json: {r1['escenas']} escenas, {r1['condiciones']} condición(es), {r1['efectos']} efecto(s)",
        f"  Finales declarados: {r1['finales_declarados']}  alcanzados por exploración: {r1['finales_alcanzados']}",
        f"  Historia oficial, finales alcanzados: {r1['finales_oficial']}",
        f"  Literales de historias en motor/*.py: {len(r1['literales_en_motor'])} {r1['literales_en_motor'] or ''}",
        "  Líneas de motor/ cambiadas en los commits que agregaron el_faro.json: "
        f"{'sin Git disponible' if r1['lineas_motor_cambiadas'] is None else r1['lineas_motor_cambiadas']}",
        "",
        f"RNF-02 Claridad de errores: {_veredicto(ok2)}",
        "  Meta: 100 % de los 10 códigos producen mensaje con causa e ID/campo, código de salida 2 y 0 tracebacks.",
        f"  Códigos cubiertos: {r2['codigos_cubiertos']}/{r2['codigos_totales']} "
        f"({100 * r2['codigos_cubiertos'] // r2['codigos_totales']} %)   "
        f"Casos correctos: {r2['casos_correctos']}/{len(r2['casos'])}   Tracebacks: {r2['tracebacks']}",
    ]
    for c in r2["casos"]:
        marca = "ok" if c["salida_2"] and c["codigo_presente"] and c["id_o_campo_presente"] and c["sin_traceback"] else "FALLA"
        l.append(f"  [{marca}] {c['caso']}: {c['mensaje']}")
    l += ["", f"RNF-03 Confiabilidad: {_veredicto(ok3)}",
          "  Meta: 1000 secuencias aleatorias de 50 acciones por historia: 0 excepciones no controladas y 0 "
          "violaciones de invariantes."]
    for r in r3:
        l += [f"  {r['historia']}: {r['secuencias']} secuencias x {r['acciones_por_secuencia']} acciones = "
              f"{r['acciones_ejecutadas']} acciones ejecutadas; excepciones: {r['excepciones']}; "
              f"violaciones: {r['violaciones']}",
              f"    Tipos de acción: {r['tipos']}",
              f"    Resultados: {r['codigos']}"]
    todo = ok1 and ok2 and ok3
    l += ["", f"Resultado global: {_veredicto(todo)}"]
    return "\n".join(l) + "\n", todo


def main() -> int:
    informe, todo = generar_informe()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(informe, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(informe)
    print(f"Guardado en {SALIDA.relative_to(RAIZ).as_posix()}")
    return 0 if todo else 1


if __name__ == "__main__":
    sys.exit(main())
