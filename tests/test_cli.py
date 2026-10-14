"""Pruebas de la interfaz de consola con entradas simuladas (sin teclado)."""
from motor.cli import Consola, main
from motor.sesion import Sesion
from tests.apoyo import RUTA_OFICIAL, historia_en_memoria, nueva_escena, nueva_opcion, sesion_oficial


def jugar(sesion, entradas):
    """Ejecuta la consola con `entradas` y devuelve (código de salida, texto mostrado)."""
    pendientes = list(entradas)
    mostrado = []

    def entrada(_prompt=""):
        if not pendientes:
            raise EOFError
        return pendientes.pop(0)

    codigo = Consola(sesion, entrada, mostrado.append).ejecutar()
    return codigo, "\n".join(mostrado)


def test_cli_muestra_titulo_escena_y_opciones_numeradas():
    """Entrada: sin elecciones. Esperado: título, texto de E1 y '1) Revisar señal'."""
    codigo, texto = jugar(sesion_oficial(), [])
    assert codigo == 0
    assert "La última transmisión" in texto
    assert "Son las 02:13" in texto
    assert "1) Revisar señal  [revisar]" in texto


def test_cli_acepta_numero_o_id_y_muestra_FIN():
    """Entrada: '1', 'investigar', '1', 'q'. Esperado: llega a E4, muestra «FIN» y termina con código 0."""
    sesion = sesion_oficial()
    codigo, texto = jugar(sesion, ["1", "investigar", "1", "q"])
    assert codigo == 0
    assert sesion.escena_actual.id == "E4"
    assert "«FIN»" in texto and "Hasta pronto." in texto


def test_cli_entradas_invalidas_se_informan_sin_cambiar_la_partida():
    """Entrada: '7', 'xyz', 'activar_codigo' en E3 sin investigar. Esperado: mensajes en español y sigue en E3."""
    sesion = sesion_oficial()
    _, texto = jugar(sesion, ["revisar", "continuar", "7", "xyz", "activar_codigo"])
    assert "No hay una opción con el número 7" in texto
    assert "La opción 'xyz' no existe en esta escena." in texto
    assert "no está disponible con la información actual" in texto
    assert sesion.escena_actual.id == "E3"


def test_cli_reiniciar_estado_y_ayuda():
    """Entrada: avanzar, 'e', '?', 'r'. Esperado: muestra variables, ayuda, 'Partida reiniciada.' y vuelve a E1."""
    sesion = sesion_oficial()
    _, texto = jugar(sesion, ["revisar", "investigar", "e", "?", "r"])
    assert "conoce_origen = verdadero" in texto
    assert "Comandos:" in texto
    assert "Partida reiniciada." in texto
    assert sesion.escena_actual.id == "E1"


def test_cli_informa_bloqueo_y_permite_reiniciar():
    """Entrada: llegar a una escena bloqueada y escribir 'r'. Esperado: mensaje de bloqueo y vuelta al inicio."""
    historia = historia_en_memoria(
        {"llave": False},
        [nueva_escena("entrada", [nueva_opcion("pasar", "puerta")]),
         nueva_escena("puerta", [nueva_opcion("abrir", "salida", {"llave": True})]),
         nueva_escena("salida")],
    )
    sesion = Sesion(historia)
    _, texto = jugar(sesion, ["pasar", "r"])
    assert "No hay opciones disponibles en esta escena." in texto
    assert sesion.escena_actual.id == "entrada"


def test_cli_fin_de_entrada_termina_de_forma_controlada():
    """Entrada: EOF inmediato. Esperado: mensaje de despedida y código 0, sin excepción."""
    codigo, texto = jugar(sesion_oficial(), [])
    assert codigo == 0 and "Fin de la entrada" in texto


def test_cli_ctrl_c_termina_de_forma_controlada(monkeypatch, capsys):
    """Entrada: KeyboardInterrupt al pedir una opción. Esperado: mensaje en español, código 130, sin traceback."""
    def interrumpir(_=""):
        raise KeyboardInterrupt
    monkeypatch.setattr("builtins.input", interrumpir)
    assert main([str(RUTA_OFICIAL)]) == 130
    assert "interrumpida" in capsys.readouterr().out


def test_cli_validar_historia_valida(capsys):
    """Entrada: --validar con la historia oficial. Esperado: 'Historia válida' y código 0."""
    assert main(["--validar", str(RUTA_OFICIAL)]) == 0
    assert "Historia válida" in capsys.readouterr().out


def test_cli_argumentos_incorrectos(capsys):
    """Entrada: argumentos no reconocidos. Esperado: mensaje de uso y código 2."""
    assert main(["--desconocido"]) == 2
    assert "Uso:" in capsys.readouterr().out
