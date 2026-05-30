# optimizacion/logger_setup.py
import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"ejecucion_{TIMESTAMP}.log")

def init_logger(console=True, level=logging.INFO):
    """Configura logger centralizado. Retorna (logger, ruta_archivo)."""
    logger = logging.getLogger("scheduling_optimizer")
    logger.setLevel(level)
    logger.handlers.clear()  # Evita duplicados en recargas

    # Handler de archivo (siempre activo)
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(fh)

    # Handler de consola (opcional)
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(ch)

    return logger, LOG_FILE