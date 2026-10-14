"""Punto de entrada: python -m motor [ruta] | python -m motor --validar ruta."""
import sys

from motor.cli import main

sys.exit(main())
