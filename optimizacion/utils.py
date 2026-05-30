import time
from optimizacion.logger_setup import init_logger

_logger, _ = init_logger(console=True)
def log(msg):
    _logger.info(msg)

def positivos_2d(diccionario):
    return {
        key for key, value in diccionario.items()
        if value == 1
    }