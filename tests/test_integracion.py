"""I1: lectura de archivos reales + motor, recorriendo hasta los finales."""
import pytest

from motor.cargador import cargar_historia
from motor.sesion import Sesion
from tests.apoyo import RUTA_FARO, RUTA_OFICIAL

RUTAS_OFICIALES = [
    (["revisar", "investigar", "activar_codigo"], "E4", {"conoce_origen": True, "confia_en_la_voz": True}),
    (["revisar", "continuar", "activar_sin_verificar"], "E5", {"conoce_origen": False, "confia_en_la_voz": True}),
    (["revisar", "investigar", "cortar"], "E6", {"conoce_origen": True, "confia_en_la_voz": False}),
    (["revisar", "continuar", "cortar"], "E6", {"conoce_origen": False, "confia_en_la_voz": False}),
]


@pytest.mark.parametrize("pasos, final, variables", RUTAS_OFICIALES, ids=["E4", "E5", "E6_investigando", "E6_sin_investigar"])
def test_I1_archivo_oficial_recorre_hasta_cada_final(pasos, final, variables):
    """Entrada: cargar historias/la_ultima_transmision.json desde disco y elegir `pasos`.
    Esperado: cada elección OK, escena final esperada, variables esperadas y FIN."""
    sesion = Sesion(cargar_historia(RUTA_OFICIAL))
    assert sesion.escena_actual.id == "E1"
    for paso in pasos:
        assert sesion.elegir(paso).ok, paso
    assert sesion.escena_actual.id == final
    assert sesion.variables == variables
    assert sesion.es_final and sesion.opciones_habilitadas() == []


RUTAS_FARO = [
    (["faro_buscar_llave", "faro_abrir_candado", "faro_encender_lampara"], "faro_rescate",
     {"tiene_llave": True, "lampara_encendida": True}),
    (["faro_buscar_llave", "faro_abrir_candado", "faro_bajar_sin_encender"], "faro_costa_oscura",
     {"tiene_llave": True, "lampara_encendida": False}),
    (["faro_ir_a_la_puerta", "faro_esperar_tormenta"], "faro_costa_oscura",
     {"tiene_llave": False, "lampara_encendida": False}),
]


@pytest.mark.parametrize("pasos, final, variables", RUTAS_FARO, ids=["rescate", "oscura_desde_lampara", "oscura_sin_llave"])
def test_I1_segunda_historia_llega_a_sus_finales_sin_cambiar_el_motor(pasos, final, variables):
    """Entrada: cargar historias/el_faro.json con el mismo motor. Esperado: llega al final indicado."""
    sesion = Sesion(cargar_historia(RUTA_FARO))
    for paso in pasos:
        assert sesion.elegir(paso).ok, paso
    assert sesion.escena_actual.id == final
    assert sesion.variables == variables
    assert sesion.es_final


def test_I1_segunda_historia_condicion_oculta_opcion_sin_llave():
    """Entrada: el_faro sin recoger la llave. Esperado: en la puerta no se ofrece abrir el candado."""
    sesion = Sesion(cargar_historia(RUTA_FARO))
    sesion.elegir("faro_ir_a_la_puerta")
    assert [o.id for o in sesion.opciones_habilitadas()] == ["faro_esperar_tormenta"]
    assert sesion.elegir("faro_abrir_candado").codigo == "OPCION_NO_HABILITADA"
