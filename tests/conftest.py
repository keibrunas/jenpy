"""
Configurazione globale per Pytest.
Aggiunge la root del progetto al PYTHONPATH per permettere gli import dei moduli app.
"""

import sys
import os

# Add the project root to the python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
