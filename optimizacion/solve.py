import time
from pathlib import Path
from optimizacion.utils import log

def exportar_modelo(model, models_dir, file_prefix):
    Path(models_dir).mkdir(parents=True, exist_ok=True)

    timestamp = f"{time.time():.2f}"
    nombre_modelo = f"{models_dir}/{file_prefix}modelo_{timestamp}.lp"

    model.write(nombre_modelo)
    log(f"Modelo LP exportado en {nombre_modelo}")

    return nombre_modelo


def optimizar(model):
    log("Iniciando optimizacion...")
    t0 = time.time()

    model.optimize()

    log(f"Optimizacion terminada en {time.time() - t0:.2f} segundos")
    log(f"Estado del modelo: {model.status}")
    log(f"Soluciones encontradas: {model.SolCount}")


def guardar_solucion(model, sols_dir, file_prefix):
    Path(sols_dir).mkdir(parents=True, exist_ok=True)

    if model.SolCount > 0:
        timestamp = f"{time.time():.2f}"
        nombre_solucion = f"{sols_dir}/{file_prefix}solucion_{timestamp}.sol"

        model.write(nombre_solucion)
        log(f"Solucion exportada en {nombre_solucion}")

        return nombre_solucion

    return None