"""Punto de entrada: python -m motor [ruta] | python -m motor --validar ruta."""
import sys

from motor.cli import configurar_salida, main

configurar_salida()
sys.exit(main())
