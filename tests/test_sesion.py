"""Pruebas unitarias de las reglas de la sesión: U1, U2, U3, U5 y bloqueo."""
import pytest

from motor.sesion import OK, OPCION_INEXISTENTE, OPCION_NO_HABILITADA, PARTIDA_FINALIZADA, SIN_RETROCESO, Sesion
from tests.apoyo import estado, historia_en_memoria, ids, nueva_escena, nueva_opcion, sesion_oficial

INICIAL = {"conoce_origen": False, "confia_en_la_voz": False}


def sesion_en_E3(investigar: bool) -> Sesion:
    sesion = sesion_oficial()
    assert sesion.elegir("revisar").ok
    assert sesion.elegir("investigar" if investigar else "continuar").ok
    return sesion


# ---------------------------------------------------------------- U1 -------

@pytest.mark.parametrize(
    "investigar, conoce_origen, esperadas",
    [
        (True, True, ["activar_codigo", "cortar"]),
        (False, False, ["activar_sin_verificar", "cortar"]),
    ],
    ids=["conoce_origen_verdadero", "conoce_origen_falso"],
)
def test_U1_condiciones_habilitan_solo_las_opciones_correspondientes_en_E3(investigar, conoce_origen, esperadas):
    """Entrada: llegar a E3 investigando o no. Esperado: exactamente cortar + la activación que corresponde."""
    sesion = sesion_en_E3(investigar)
    assert sesion.escena_actual.id == "E3"
    assert sesion.variables["conoce_origen"] is conoce_origen
    assert ids(sesion.opciones_habilitadas()) == esperadas


def test_U1_CA01_revisar_e_investigar_muestra_activar_con_codigo_y_cortar():
    """CA01. Entrada: partida nueva, revisar + investigar. Esperado: E3, conoce_origen verdadero, 2 opciones."""
    sesion = sesion_en_E3(investigar=True)
    assert estado(sesion) == ("E3", {"conoce_origen": True, "confia_en_la_voz": False})
    assert set(ids(sesion.opciones_habilitadas())) == {"activar_codigo", "cortar"}


@pytest.mark.parametrize(
    "a, b, habilitada",
    [(True, True, True), (True, False, False), (False, True, False), (False, False, False)],
)
def test_U1_todas_las_condiciones_deben_cumplirse(a, b, habilitada):
    """Entrada: opción con condiciones {a: true, b: true} y valores iniciales (a, b). Esperado: habilitada solo si ambas."""
    historia = historia_en_memoria(
        {"a": a, "b": b},
        [
            nueva_escena("inicio", [nueva_opcion("doble", "fin", {"a": True, "b": True}), nueva_opcion("libre", "fin")]),
            nueva_escena("fin"),
        ],
    )
    visibles = ids(Sesion(historia).opciones_habilitadas())
    assert ("doble" in visibles) is habilitada
    assert "libre" in visibles  # condiciones vacías: siempre habilitada


# ---------------------------------------------------------------- U2 -------

def test_U2_eleccion_valida_aplica_efectos_y_avanza_al_destino():
    """Entrada: en E2 elegir investigar. Esperado: resultado OK, escena E3 y conoce_origen verdadero."""
    sesion = sesion_oficial()
    sesion.elegir("revisar")
    resultado = sesion.elegir("investigar")
    assert resultado.codigo == OK
    assert estado(sesion) == ("E3", {"conoce_origen": True, "confia_en_la_voz": False})


def test_U2_efectos_vacios_conservan_las_variables():
    """Entrada: revisar (E1) y continuar (E2), ambas sin efectos. Esperado: variables iguales a las iniciales."""
    sesion = sesion_oficial()
    assert sesion.elegir("revisar").codigo == OK
    assert estado(sesion) == ("E2", INICIAL)
    assert sesion.elegir("continuar").codigo == OK
    assert estado(sesion) == ("E3", INICIAL)


@pytest.mark.parametrize(
    "investigar, id_opcion, destino, confia",
    [
        (True, "activar_codigo", "E4", True),
        (False, "activar_sin_verificar", "E5", True),
        (True, "cortar", "E6", False),
    ],
)
def test_U2_cada_opcion_de_E3_lleva_a_su_final_con_su_efecto(investigar, id_opcion, destino, confia):
    """Entrada: elegir una opción habilitada de E3. Esperado: destino y confia_en_la_voz según la tabla de la guía."""
    sesion = sesion_en_E3(investigar)
    assert sesion.elegir(id_opcion).codigo == OK
    assert sesion.escena_actual.id == destino
    assert sesion.variables["confia_en_la_voz"] is confia
    assert sesion.es_final


# ---------------------------------------------------------------- U3 -------

@pytest.mark.parametrize("id_opcion", ["no_existe", "", "revisar", "E4", "1"])
def test_U3_opcion_inexistente_deja_intacto_el_estado(id_opcion):
    """Entrada: en E3 un ID que no es opción de la escena. Esperado: OPCION_INEXISTENTE y estado idéntico."""
    sesion = sesion_en_E3(investigar=True)
    antes = estado(sesion)
    resultado = sesion.elegir(id_opcion)
    assert resultado.codigo == OPCION_INEXISTENTE
    assert estado(sesion) == antes


def test_U3_CA02_activar_codigo_sin_conocer_origen_se_rechaza():
    """CA02. Entrada: E3 sin investigar y enviar 'activar_codigo' directo al motor.
    Esperado: OPCION_NO_HABILITADA, estado idéntico; después activar_sin_verificar lleva a E5."""
    sesion = sesion_en_E3(investigar=False)
    antes = estado(sesion)
    resultado = sesion.elegir("activar_codigo")
    assert resultado.codigo == OPCION_NO_HABILITADA
    assert "activar_codigo" in resultado.mensaje
    assert estado(sesion) == antes
    assert sesion.elegir("activar_sin_verificar").codigo == OK
    assert sesion.escena_actual.id == "E5"


def test_U3_elegir_en_un_final_devuelve_partida_finalizada():
    """Entrada: en E6 intentar 'cortar' y 'revisar'. Esperado: PARTIDA_FINALIZADA y estado idéntico."""
    sesion = sesion_en_E3(investigar=True)
    sesion.elegir("cortar")
    antes = estado(sesion)
    for id_opcion in ("cortar", "revisar"):
        assert sesion.elegir(id_opcion).codigo == PARTIDA_FINALIZADA
        assert estado(sesion) == antes
    assert sesion.opciones_habilitadas() == []


def test_U3_variables_expuestas_son_copia_y_la_historia_no_cambia():
    """Entrada: modificar el dict devuelto por variables. Esperado: la sesión y la historia no cambian."""
    sesion = sesion_oficial()
    copia = sesion.variables
    copia["conoce_origen"] = True
    assert sesion.variables["conoce_origen"] is False
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    assert dict(sesion.historia.variables) == INICIAL


# ---------------------------------------------------------------- U5 -------

@pytest.mark.parametrize("pasos", [[], ["revisar"], ["revisar", "investigar"], ["revisar", "investigar", "activar_codigo"]])
def test_U5_reiniciar_restaura_escena_y_variables_iniciales(pasos):
    """Entrada: avanzar con `pasos` y reiniciar. Esperado: escena E1 y variables iniciales."""
    sesion = sesion_oficial()
    for paso in pasos:
        assert sesion.elegir(paso).ok
    sesion.reiniciar()
    assert estado(sesion) == ("E1", INICIAL)
    assert ids(sesion.opciones_habilitadas()) == ["revisar"]


def test_U5_reiniciar_no_conserva_informacion_de_la_partida_anterior():
    """Entrada: terminar en E4 (conoce_origen verdadero), reiniciar y continuar sin investigar.
    Esperado: en E3 aparece activar_sin_verificar, no activar_codigo."""
    sesion = sesion_en_E3(investigar=True)
    sesion.elegir("activar_codigo")
    sesion.reiniciar()
    sesion.elegir("revisar")
    sesion.elegir("continuar")
    assert ids(sesion.opciones_habilitadas()) == ["activar_sin_verificar", "cortar"]


@pytest.mark.parametrize("pasos", [["revisar"], ["revisar", "investigar"], ["revisar", "investigar", "activar_codigo"]])
def test_U5_extendido_reiniciar_elimina_el_historial_de_deshacer(pasos):
    """Entrada (cambio): avanzar con `pasos` (hay retroceso disponible) y reiniciar.
    Esperado: puede_deshacer falso, deshacer devuelve SIN_RETROCESO y el estado sigue siendo el inicial."""
    sesion = sesion_oficial()
    for paso in pasos:
        sesion.elegir(paso)
    assert sesion.puede_deshacer
    sesion.reiniciar()
    assert not sesion.puede_deshacer
    assert sesion.deshacer().codigo == SIN_RETROCESO
    assert estado(sesion) == ("E1", INICIAL)


# ----------------------------------------------------------- Bloqueo -------

def historia_con_bloqueo():
    return historia_en_memoria(
        {"llave": False},
        [
            nueva_escena("entrada", [nueva_opcion("pasar", "puerta")]),
            nueva_escena("puerta", [nueva_opcion("abrir", "salida", condiciones={"llave": True})]),
            nueva_escena("salida"),
        ],
    )


def test_bloqueo_escena_no_final_sin_opciones_habilitadas():
    """Entrada: llegar a 'puerta' sin llave. Esperado: esta_bloqueada, no es final, 0 opciones y 'abrir' rechazada."""
    sesion = Sesion(historia_con_bloqueo())
    assert not sesion.esta_bloqueada
    sesion.elegir("pasar")
    assert sesion.esta_bloqueada
    assert not sesion.es_final
    assert sesion.opciones_habilitadas() == []
    assert sesion.elegir("abrir").codigo == OPCION_NO_HABILITADA
    assert estado(sesion) == ("puerta", {"llave": False})


def test_bloqueo_reiniciar_sale_del_bloqueo():
    """Entrada: sesión bloqueada y reiniciar. Esperado: escena inicial sin bloqueo."""
    sesion = Sesion(historia_con_bloqueo())
    sesion.elegir("pasar")
    sesion.reiniciar()
    assert estado(sesion) == ("entrada", {"llave": False})
    assert not sesion.esta_bloqueada


def test_bloqueo_deshacer_vuelve_a_la_escena_anterior():
    """Entrada (cambio): sesión bloqueada en 'puerta' y deshacer. Esperado: vuelve a 'entrada' sin bloqueo."""
    sesion = Sesion(historia_con_bloqueo())
    sesion.elegir("pasar")
    assert sesion.esta_bloqueada and sesion.puede_deshacer
    assert sesion.deshacer().codigo == OK
    assert estado(sesion) == ("entrada", {"llave": False})
    assert not sesion.esta_bloqueada
