"""Verificación automatizada de los RNF (los mismos procedimientos que scripts/verificar_rnf.py)."""
import pytest

from motor.cargador import cargar_historia
from scripts.verificar_rnf import (
    ejecutar_motor,
    evaluar_caso_invalido,
    finales_alcanzables,
    literales_de_historias_en_motor,
    lineas_de_motor_cambiadas_al_agregar,
    secuencias_aleatorias,
)
from tests.apoyo import CASOS_INVALIDOS, RUTA_DESTINO_INEXISTENTE, RUTA_FARO, RUTA_OFICIAL


# ---------------------------------------------------------------- RNF-01 ---

def test_RNF01_segunda_historia_cumple_el_tamano_minimo():
    """Entrada: el_faro.json. Esperado: >= 3 escenas, >= 1 condición, >= 1 efecto, >= 2 finales."""
    historia = cargar_historia(RUTA_FARO)
    opciones = [o for e in historia.escenas for o in e.opciones]
    assert len(historia.escenas) >= 3
    assert any(o.condiciones for o in opciones)
    assert any(o.efectos for o in opciones)
    assert sum(e.final for e in historia.escenas) >= 2


@pytest.mark.parametrize("ruta", [RUTA_FARO, RUTA_OFICIAL], ids=["el_faro", "oficial"])
def test_RNF01_todos_los_finales_son_alcanzables_con_el_mismo_motor(ruta):
    """Entrada: explorar todas las elecciones posibles con Sesion. Esperado: se alcanzan todos los finales declarados."""
    historia = cargar_historia(ruta)
    assert finales_alcanzables(historia) == {e.id for e in historia.escenas if e.final}


def test_RNF01_el_motor_no_contiene_ids_ni_variables_de_las_historias():
    """Entrada: motor/*.py y los IDs/variables de ambas historias. Esperado: 0 apariciones."""
    assert literales_de_historias_en_motor() == []


def test_RNF01_agregar_la_segunda_historia_no_cambio_lineas_del_motor():
    """Entrada: commits de Git que tocaron historias/el_faro.json. Esperado: 0 líneas de motor/ en esos commits."""
    cambiadas = lineas_de_motor_cambiadas_al_agregar(RUTA_FARO)
    if cambiadas is None:
        pytest.skip("Git o el historial no están disponibles en esta copia")
    assert cambiadas == 0


# ---------------------------------------------------------------- RNF-02 ---

@pytest.mark.parametrize("caso", CASOS_INVALIDOS, ids=[c.nombre for c in CASOS_INVALIDOS])
def test_RNF02_validar_por_consola_da_mensaje_con_id_y_sin_traceback(caso, tmp_path):
    """Entrada: `python -m motor --validar <archivo inválido>` en un proceso aparte.
    Esperado: código de salida 2, el código de error, el ID/campo afectado y ningún 'Traceback'."""
    resultado = evaluar_caso_invalido(caso, tmp_path)
    assert resultado["salida_2"], resultado
    assert resultado["codigo_presente"], resultado
    assert resultado["id_o_campo_presente"], resultado
    assert resultado["sin_traceback"], resultado


def test_RNF02_CA03_jugar_un_destino_inexistente_no_abre_la_partida():
    """CA03. Entrada: `python -m motor historias/invalidas/destino_inexistente.json`.
    Esperado: código 2, mensaje con E99 y sin mostrar el texto de la primera escena."""
    proceso = ejecutar_motor(str(RUTA_DESTINO_INEXISTENTE))
    assert proceso.returncode == 2
    assert "E99" in proceso.stdout and "DESTINO_INEXISTENTE" in proceso.stdout
    assert "Son las 02:13" not in proceso.stdout
    assert "Traceback" not in proceso.stdout + proceso.stderr


def test_RNF02_jugar_por_consola_hasta_un_final_sin_traceback():
    """Entrada: proceso real con entradas válidas, inválidas y deshacer por stdin. Esperado: llega a «FIN», código 0."""
    proceso = ejecutar_motor(str(RUTA_OFICIAL), entrada="revisar\nxyz\n9\ninvestigar\nd\ninvestigar\n1\n")
    assert proceso.returncode == 0
    assert "«FIN»" in proceso.stdout and "[E4]" in proceso.stdout
    assert "Traceback" not in proceso.stdout + proceso.stderr


# ---------------------------------------------------------------- RNF-03 ---

@pytest.mark.parametrize("ruta", [RUTA_OFICIAL, RUTA_FARO], ids=["oficial", "el_faro"])
def test_RNF03_mil_secuencias_aleatorias_sin_excepciones_ni_violaciones(ruta):
    """Entrada: 1000 secuencias con semilla fija de 50 acciones (IDs válidos, inválidos, texto aleatorio,
    deshacer, reiniciar). Esperado: 50 000 acciones ejecutadas, 0 excepciones y 0 violaciones de invariantes."""
    resultado = secuencias_aleatorias(cargar_historia(ruta), secuencias=1000, acciones=50)
    assert resultado["acciones_ejecutadas"] == 50_000
    assert resultado["excepciones"] == 0
    assert resultado["violaciones"] == 0
    assert set(resultado["tipos"]) == {"valida", "id_cualquiera", "texto_aleatorio", "deshacer", "reiniciar"}
