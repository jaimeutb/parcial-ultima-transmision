"""Coherencia de la documentación con la versión entregada (lista de revisión de la guía, §8).

Cada nombre citado en la matriz de trazabilidad y en el diagrama de clases debe existir en el código.
"""
import re

import pytest

import motor.cli
import motor.modelo
import motor.sesion
import motor.validador
from tests.apoyo import RAIZ

TRAZABILIDAD = (RAIZ / "docs" / "trazabilidad.md").read_text(encoding="utf-8")
MODELOS = (RAIZ / "docs" / "modelos.md").read_text(encoding="utf-8")
FUENTES = {p: p.read_text(encoding="utf-8") for d in ("motor", "scripts", "tests") for p in (RAIZ / d).glob("*.py")}
PRUEBAS = {m for p, s in FUENTES.items() if p.parent.name == "tests" for m in re.findall(r"^def (test_\w+)", s, re.M)}
CLASES = {
    "Historia": motor.modelo.Historia, "Escena": motor.modelo.Escena, "Opcion": motor.modelo.Opcion,
    "Sesion": motor.sesion.Sesion, "ResultadoAccion": motor.sesion.ResultadoAccion,
    "ErrorContenido": motor.validador.ErrorContenido, "HistoriaInvalida": motor.validador.HistoriaInvalida,
    "Consola": motor.cli.Consola,
}
REFERENCIAS = sorted(set(re.findall(r"`([^`\s]+)`", TRAZABILIDAD)))


def existe_prueba(nombre: str) -> bool:
    nombre = nombre.split("[")[0]
    if nombre.endswith("*"):
        return any(p.startswith(nombre[:-1]) for p in PRUEBAS)
    return nombre in PRUEBAS


def existe_simbolo(nombre: str) -> bool:
    """Busca una función, clase, método o atributo (p. ej. `Sesion._anterior`) en el código fuente."""
    ultimo = nombre.split(".")[-1]
    patron = rf"(def |class |self\.){re.escape(ultimo)}\b|^\s*{re.escape(ultimo)}\s*[:=]"
    return any(re.search(patron, s, re.M) for s in FUENTES.values())


@pytest.mark.parametrize("referencia", REFERENCIAS)
def test_trazabilidad_cada_referencia_existe_en_la_version_entregada(referencia):
    """Entrada: cada nombre entre comillas invertidas de docs/trazabilidad.md.
    Esperado: el archivo, la prueba o el símbolo citado existe en el repositorio."""
    if referencia == "archivo::función":  # ejemplo de formato en el encabezado de la matriz
        return
    if "::" in referencia:
        archivo, simbolo = referencia.split("::", 1)
        ruta = RAIZ / archivo if "/" in archivo else RAIZ / "tests" / archivo
        assert ruta.exists(), archivo
        if simbolo.startswith("test_"):
            assert existe_prueba(simbolo), referencia
        else:
            assert existe_simbolo(simbolo), referencia
    elif referencia.startswith("test_"):
        assert existe_prueba(referencia), referencia
    elif re.search(r"\.(py|json|md|txt)$", referencia) or referencia.endswith("/"):
        assert (RAIZ / referencia).exists(), referencia
    elif re.fullmatch(r"[A-Za-z_][\w.]*", referencia):
        # Nombres de elementos de modelo (estados, fragmentos de secuencia) o símbolos del código.
        en_modelos = re.search(r"(?<!\w)" + re.escape(referencia) + r"(?!\w)", MODELOS)
        assert existe_simbolo(referencia) or en_modelos, referencia


def test_trazabilidad_incluye_todos_los_rf_y_rnf():
    """Entrada: requisitos.md y trazabilidad.md. Esperado: cada RF y RNF definido tiene su fila en la matriz."""
    requisitos = (RAIZ / "docs" / "requisitos.md").read_text(encoding="utf-8")
    definidos = set(re.findall(r"^\| (RF\d\d|RNF-\d\d) ", requisitos, re.M))
    en_matriz = set(re.findall(r"^\| \**(RF\d\d|RNF-\d\d)", TRAZABILIDAD, re.M))
    assert len(definidos) == 20 and definidos == en_matriz


def miembros_del_diagrama() -> list[tuple[str, str]]:
    diagrama = re.search(r"```mermaid\nclassDiagram(.*?)```", MODELOS, re.S).group(1)
    miembros = []
    for clase, cuerpo in re.findall(r"class (\w+) \{(.*?)\}", diagrama, re.S):
        for linea in cuerpo.strip().splitlines():
            miembros.append((clase, re.match(r"\s*[+-](\w+)", linea).group(1)))
    return miembros


@pytest.mark.parametrize("clase, miembro", miembros_del_diagrama())
def test_modelo_de_clases_coincide_con_el_codigo(clase, miembro):
    """Entrada: cada atributo/método del diagrama de clases. Esperado: existe en la clase del código."""
    tipo = CLASES[clase]
    campos = getattr(tipo, "__dataclass_fields__", {})
    assert hasattr(tipo, miembro) or miembro in campos or existe_simbolo(f"{clase}.{miembro}"), f"{clase}.{miembro}"
