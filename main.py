import logging
import sys
import time

from gurobipy import GRB

from optimizacion.config import (
    DATA_REAL,
    MODELS_DIR,
    SOLS_DIR,
    FILE_PREFIX,
    LIMPIEZA_BLOQUES,
    EXPORTAR_LP,
    USAR_WARM_START,
)
from optimizacion.logger_setup import init_logger, LOG_FILE
from optimizacion.utils import log
from optimizacion.data_loader import cargar_datos
from optimizacion.preprocessing import preparar_prefiltering
from optimizacion.gurobi_config import crear_modelo
from optimizacion.reporting import (
    imprimir_resumen_conjuntos,
    imprimir_resumen_variables,
    mostrar_resultados,
)
from optimizacion.solve import exportar_modelo, optimizar, guardar_solucion

from variables import crear_variables
from restricciones import agregar_restricciones
from funcion_objetivo import agregar_funcion_objetivo

try:
    from optimizacion.warm_start import aplicar_warm_start_factible
    WARM_START_DISPONIBLE = True
except ImportError:
    WARM_START_DISPONIBLE = False


def main():
    inicio_total = time.time()
    logger, log_path = init_logger(console=True, level=logging.INFO)
    class PrintRedirector:
        def __init__(self, logger, level=logging.INFO):
            self.logger, self.level = logger, level
        def write(self, msg):
            if msg.strip(): self.logger.log(self.level, msg.strip())
        def flush(self): pass
    
    sys.stdout = PrintRedirector(logger)
    sys.stderr = PrintRedirector(logger, logging.ERROR)

    log("Iniciando modelo de programacion quirurgica")
    log(f"Modo de datos: {'Real' if DATA_REAL else 'Sintetico'}")

    conjuntos, parametros = cargar_datos(DATA_REAL)
    prefilter = preparar_prefiltering(
        pacientes=conjuntos["pacientes"],
        G=parametros["G"],
        DispP=parametros["DispP"],
        DispK=parametros["DispK"],
        DispM=parametros["DispM"],
        Q=parametros["Q"],
        A=parametros["A"],
    )
    imprimir_resumen_conjuntos(conjuntos, prefilter)

    model = crear_modelo()

    X, ZI, Z, LQ, WI, W, Y, H, O = crear_variables(
        model=model,
        pacientes=conjuntos["pacientes"],
        tiempos=conjuntos["tiempos"],
        pabellones=conjuntos["pabellones"],
        camas=conjuntos["camas"],
        cirujanos=conjuntos["cirujanos"],
        anestesistas=conjuntos["anestesistas"],
        ci_paciente=prefilter["ci_paciente"],
        duracion_cirugia=parametros["d"],
        duracion_recuperacion=parametros["r"],
        limpieza=LIMPIEZA_BLOQUES,
        DispP_pos=prefilter["DispP_pos"],
        DispK_pos=prefilter["DispK_pos"],
        DispM_pos=prefilter["DispM_pos"],
        CK_pos=prefilter["CK_pos"],
        CM_pos=prefilter["CM_pos"],
    )

    log(f"Numero de variables: {model.NumVars}")
    imprimir_resumen_variables(X, ZI, Z, LQ, WI, W, Y, H, O)

    agregar_restricciones(
        model=model, X=X, ZI=ZI, Z=Z, LQ=LQ, WI=WI, W=W, Y=Y, H=H, O=O,
        pacientes=conjuntos["pacientes"], tiempos=conjuntos["tiempos"],
        pabellones=conjuntos["pabellones"], camas=conjuntos["camas"],
        cirujanos=conjuntos["cirujanos"], anestesistas=conjuntos["anestesistas"],
        cirugias=conjuntos["cirugias"], especialidades=conjuntos["especialidades"],
        G=parametros["G"], E=parametros["E"], A=parametros["A"], Q=parametros["Q"],
        R=parametros["R"], DispP=parametros["DispP"], DispK=parametros["DispK"],
        DispM=parametros["DispM"], d=parametros["d"], r=parametros["r"],
        L=parametros["L"], a=parametros["a"], b=parametros["b"], usar_update_final=True,
    )

    agregar_funcion_objetivo(
        model=model, X=X, O=O, pacientes=conjuntos["pacientes"],
        pabellones=conjuntos["pabellones"], tiempos=conjuntos["tiempos"],
        w=parametros["w"], alpha=parametros["alpha"],
    )

    if USAR_WARM_START and WARM_START_DISPONIBLE:
        log("Aplicando warm start factible...")
        aplicar_warm_start_factible(
            X=X, ZI=ZI, Z=Z, LQ=LQ, WI=WI, W=W, Y=Y, H=H, O=O,
            pacientes=conjuntos["pacientes"], tiempos=conjuntos["tiempos"],
            pabellones=conjuntos["pabellones"], camas=conjuntos["camas"],
            cirujanos=conjuntos["cirujanos"], anestesistas=conjuntos["anestesistas"],
            d=parametros["d"], r=parametros["r"], L=parametros["L"],
            G=parametros["G"], cirugias=conjuntos["cirugias"],
            DispP=parametros["DispP"], E=parametros["E"], A=parametros["A"],
            a=parametros["a"], b=parametros["b"], especialidades=conjuntos["especialidades"],
            max_pacientes=None, verbose=True,
        )

    model.update()

    if EXPORTAR_LP:
        exportar_modelo(model, MODELS_DIR, FILE_PREFIX)

    optimizar(model)

    mostrar_resultados(
        model=model, X=X, ZI=ZI, WI=WI, Y=Y, H=H, conjuntos=conjuntos,
    )
    guardar_solucion(model, SOLS_DIR, FILE_PREFIX)

    log(f"Tiempo total de ejecucion: {time.time() - inicio_total:.2f} segundos")
    model.dispose()

if __name__ == "__main__":
    main()