"""U6 (solicitud de cambio): deshacer restaura escena y variables y consume el retroceso."""
import pytest

from motor.sesion import OK, OPCION_INEXISTENTE, OPCION_NO_HABILITADA, SIN_RETROCESO
from tests.apoyo import estado, ids, sesion_oficial

INICIAL = {"conoce_origen": False, "confia_en_la_voz": False}


def test_U6_ejemplo_del_docente_investigar_deshacer_y_continuar():
    """Entrada (ejemplo de la solicitud): en E2 investigar, deshacer, deshacer otra vez, continuar.
    Esperado: E3 con conoce_origen verdadero; E2 con falso; el segundo deshacer devuelve SIN_RETROCESO
    sin cambios; E3 muestra exactamente activar_sin_verificar y cortar."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    assert estado(sesion) == ("E2", INICIAL)

    assert sesion.elegir("investigar").codigo == OK
    assert estado(sesion) == ("E3", {"conoce_origen": True, "confia_en_la_voz": False})

    assert sesion.deshacer().codigo == OK
    assert estado(sesion) == ("E2", INICIAL)
    assert not sesion.puede_deshacer

    segundo = sesion.deshacer()
    assert segundo.codigo == SIN_RETROCESO
    assert estado(sesion) == ("E2", INICIAL)

    assert sesion.elegir("continuar").codigo == OK
    assert estado(sesion) == ("E3", INICIAL)
    assert ids(sesion.opciones_habilitadas()) == ["activar_sin_verificar", "cortar"]


def test_U6_al_comenzar_no_hay_retroceso():
    """Entrada: sesión nueva y deshacer. Esperado: puede_deshacer falso, SIN_RETROCESO y E1 intacto."""
    sesion = sesion_oficial()
    assert not sesion.puede_deshacer
    assert sesion.deshacer().codigo == SIN_RETROCESO
    assert estado(sesion) == ("E1", INICIAL)


@pytest.mark.parametrize(
    "invalida, codigo",
    [("no_existe", OPCION_INEXISTENTE), ("activar_sin_verificar", OPCION_NO_HABILITADA)],
    ids=["inexistente", "no_habilitada"],
)
def test_U6_entrada_invalida_preserva_el_historial(invalida, codigo):
    """Entrada: investigar (E2→E3), una entrada inválida en E3 y deshacer.
    Esperado: la entrada inválida se rechaza sin tocar el historial; deshacer vuelve a E2 con valores previos."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    antes = estado(sesion)
    assert sesion.elegir(invalida).codigo == codigo
    assert estado(sesion) == antes
    assert sesion.puede_deshacer
    assert sesion.deshacer().codigo == OK
    assert estado(sesion) == ("E2", INICIAL)


def test_U6_elegir_en_un_final_no_borra_el_historial():
    """Entrada: llegar a E4, intentar elegir 'activar_codigo' y 'xyz' (PARTIDA_FINALIZADA) y deshacer.
    Esperado: los intentos no cambian nada y deshacer sigue volviendo a E3 con los valores previos."""
    sesion = sesion_oficial()
    for paso in ("revisar", "investigar", "activar_codigo"):
        sesion.elegir(paso)
    for intento in ("activar_codigo", "xyz"):
        assert sesion.elegir(intento).codigo == "PARTIDA_FINALIZADA"
    assert sesion.puede_deshacer
    assert sesion.deshacer().codigo == OK
    assert estado(sesion) == ("E3", {"conoce_origen": True, "confia_en_la_voz": False})


def test_U6_nueva_eleccion_valida_vuelve_a_habilitar_el_retroceso():
    """Entrada: investigar, deshacer, investigar de nuevo, deshacer. Esperado: el segundo deshacer funciona."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    sesion.deshacer()
    assert not sesion.puede_deshacer
    assert sesion.elegir("investigar").codigo == OK
    assert sesion.puede_deshacer
    assert sesion.deshacer().codigo == OK
    assert estado(sesion) == ("E2", INICIAL)


def test_U6_solo_un_nivel_vuelve_a_la_escena_previa_a_la_ultima_eleccion():
    """Entrada: revisar, investigar, deshacer, deshacer. Esperado: vuelve a E2 (no a E1) y luego SIN_RETROCESO."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    sesion.deshacer()
    assert sesion.escena_actual.id == "E2"
    assert sesion.deshacer().codigo == SIN_RETROCESO
    assert sesion.escena_actual.id == "E2"


def test_U6_restaura_todas_las_variables():
    """Entrada: E3 tras investigar; cortar (confia_en_la_voz=falso) y activar_codigo (confia=verdadero), deshaciendo.
    Esperado: tras cada deshacer, conoce_origen y confia_en_la_voz vuelven a sus valores previos."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    previo = {"conoce_origen": True, "confia_en_la_voz": False}
    sesion.elegir("activar_codigo")
    assert sesion.variables == {"conoce_origen": True, "confia_en_la_voz": True}
    sesion.deshacer()
    assert sesion.variables == previo
    assert sesion.variables["confia_en_la_voz"] is False


def test_U6_la_instantanea_es_una_copia_y_no_una_referencia():
    """Entrada: tras una elección, modificar la copia expuesta de variables y elegir/deshacer de nuevo.
    Esperado: el estado restaurado no se ve afectado por cambios posteriores ni comparte objetos."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    externas = sesion.variables
    externas["conoce_origen"] = True
    sesion.elegir("investigar")
    assert sesion.variables["conoce_origen"] is True
    sesion.deshacer()
    assert sesion.variables == INICIAL
    restauradas = sesion.variables
    restauradas["confia_en_la_voz"] = True
    sesion.elegir("investigar")
    sesion.deshacer()
    assert sesion.variables == INICIAL


@pytest.mark.parametrize(
    "camino, final, previo",
    [
        (["investigar", "activar_codigo"], "E4", {"conoce_origen": True, "confia_en_la_voz": False}),
        (["continuar", "activar_sin_verificar"], "E5", {"conoce_origen": False, "confia_en_la_voz": False}),
        (["investigar", "cortar"], "E6", {"conoce_origen": True, "confia_en_la_voz": False}),
    ],
    ids=["E4", "E5", "E6"],
)
def test_U6_desde_un_final_vuelve_a_E3_con_valores_previos(camino, final, previo):
    """Entrada: llegar a un final y deshacer. Esperado: E3, variables previas y opciones de E3 otra vez disponibles."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    for paso in camino:
        sesion.elegir(paso)
    assert sesion.escena_actual.id == final and sesion.es_final
    assert sesion.deshacer().codigo == OK
    assert estado(sesion) == ("E3", previo)
    assert not sesion.es_final
    assert camino[-1] in ids(sesion.opciones_habilitadas())
