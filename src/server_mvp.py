"""
Proyecto PTIA - Grupo 2: RacePulse AI (Hito 3 - Servidor MVP Funcional)
Punto de entrada compatible que ejecuta la aplicación FastAPI oficial en http://localhost:8000
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app

if __name__ == "__main__":
    app.main()
