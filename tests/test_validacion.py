"""U4: los errores de contenido producen rechazo con diagnóstico controlado."""
import pytest

from motor.cargador import cargar_historia
from motor.cli import main
from motor.validador import CODIGOS_ERROR, ErrorContenido, HistoriaInvalida, validar
from tests.apoyo import CASOS_INVALIDOS, RUTA_FARO, RUTA_OFICIAL, datos_oficiales, escena, escribir_json, opcion


@pytest.mark.parametrize("caso", CASOS_INVALIDOS, ids=[c.nombre for c in CASOS_INVALIDOS])
def test_U4_contenido_invalido_se_rechaza_con_codigo_causa_y_ubicacion(caso, tmp_path):
    """Entrada: archivo con un defecto (uno por variante). Esperado: HistoriaInvalida con el código
    del caso y un mensaje/ubicación que menciona el ID o campo afectado; no se obtiene una Historia."""
    ruta = caso.preparar(tmp_path)
    with pytest.raises(HistoriaInvalida) as info:
        cargar_historia(ruta)
    errores = info.value.errores
    assert errores and all(isinstance(e, ErrorContenido) and e.mensaje for e in errores)
    del_caso = [e for e in errores if e.codigo == caso.codigo]
    assert del_caso, f"Se esperaba {caso.codigo}; se obtuvo {[str(e) for e in errores]}"
    assert any(all(f in f"{e.mensaje} {e.ubicacion}" for f in caso.fragmentos) for e in del_caso)


def test_U4_los_casos_cubren_los_diez_codigos_de_error():
    """Entrada: lista de casos parametrizados. Esperado: al menos un caso por cada código definido."""
    assert {c.codigo for c in CASOS_INVALIDOS} == set(CODIGOS_ERROR)


@pytest.mark.parametrize("caso", CASOS_INVALIDOS, ids=[c.nombre for c in CASOS_INVALIDOS])
def test_U4_historia_invalida_no_abre_sesion_jugable(caso, tmp_path, monkeypatch, capsys):
    """Entrada: `python -m motor <archivo inválido>` (vía main). Esperado: código 2, errores listados,
    nunca se pide una elección al lector (no hay sesión)."""
    def entrada_prohibida(_=""):
        raise AssertionError("Se abrió una sesión con una historia inválida")
    monkeypatch.setattr("builtins.input", entrada_prohibida)
    assert main([str(caso.preparar(tmp_path))]) == 2
    salida = capsys.readouterr().out
    assert caso.codigo in salida and "no es válida" in salida


def test_U4_se_informan_todos_los_errores_a_la_vez(tmp_path):
    """Entrada: archivo con tres defectos distintos. Esperado: los tres códigos en una sola validación."""
    datos = datos_oficiales()
    datos["inicio"] = "E0"
    opcion(datos, "E2", "investigar")["destino"] = "E99"
    escena(datos, "E6")["final"] = 1
    with pytest.raises(HistoriaInvalida) as info:
        cargar_historia(escribir_json(tmp_path, "varios.json", datos))
    codigos = {e.codigo for e in info.value.errores}
    assert {"INICIO_INEXISTENTE", "DESTINO_INEXISTENTE", "ESTRUCTURA_INVALIDA"} <= codigos


@pytest.mark.parametrize("valor", [0, 1, "true", "false", None])
def test_U4_valores_parecidos_a_booleanos_se_rechazan(valor):
    """Entrada: variable inicial con 0, 1, "true", "false" o null. Esperado: VALOR_NO_BOOLEANO."""
    datos = datos_oficiales()
    datos["variables"]["confia_en_la_voz"] = valor
    assert [e.codigo for e in validar(datos)] == ["VALOR_NO_BOOLEANO"]


@pytest.mark.parametrize("ruta", [RUTA_OFICIAL, RUTA_FARO], ids=["oficial", "el_faro"])
def test_U4_historias_validas_no_producen_errores(ruta):
    """Entrada: las dos historias entregadas. Esperado: 0 errores y modelo construido."""
    historia = cargar_historia(ruta)
    assert historia.escenas
