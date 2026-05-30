import logging
from gurobipy import GRB

# Usa el mismo nombre que definiste en logger_setup.py
logger = logging.getLogger("scheduling_optimizer")

def imprimir_resumen_conjuntos(conjuntos, prefilter):
    logger.info("Resumen de conjuntos:")
    logger.info(f"Pacientes: {len(conjuntos['pacientes'])}")
    logger.info(f"Tiempos: {len(conjuntos['tiempos'])}")
    logger.info(f"Pabellones: {len(conjuntos['pabellones'])}")
    logger.info(f"Camas: {len(conjuntos['camas'])}")
    logger.info(f"Cirujanos: {len(conjuntos['cirujanos'])}")
    logger.info(f"Anestesistas: {len(conjuntos['anestesistas'])}")
    logger.info(f"Tipos de cirugia: {len(conjuntos['cirugias'])}")
    logger.info(f"Especialidades: {len(conjuntos['especialidades'])}")

    logger.info("Resumen de pre-filtering:")
    logger.info(f"Pacientes con cirugía asignada: {len(prefilter['ci_paciente'])}")
    logger.info(f"Disponibilidad pabellones positiva: {len(prefilter['DispP_pos'])}")
    logger.info(f"Disponibilidad cirujanos positiva: {len(prefilter['DispK_pos'])}")
    logger.info(f"Disponibilidad anestesistas positiva: {len(prefilter['DispM_pos'])}")
    logger.info(f"Compatibilidad cirugía-cirujano positiva: {len(prefilter['CK_pos'])}")
    logger.info(f"Compatibilidad cirugía-anestesista positiva: {len(prefilter['CM_pos'])}")


def imprimir_resumen_variables(X, ZI, Z, LQ, WI, W, Y, H, O):
    logger.info("Detalle de variables:")
    logger.info(f"X:  {len(X)}")
    logger.info(f"ZI: {len(ZI)}")
    logger.info(f"Z:  {len(Z)}")
    logger.info(f"LQ: {len(LQ)}")
    logger.info(f"WI: {len(WI)}")
    logger.info(f"W:  {len(W)}")
    logger.info(f"Y:  {len(Y)}")
    logger.info(f"H:  {len(H)}")
    logger.info(f"O:  {len(O)}")


def mostrar_resultados(model, X, ZI, WI, Y, H, conjuntos):
    pacientes = conjuntos["pacientes"]
    tiempos = conjuntos["tiempos"]
    pabellones = conjuntos["pabellones"]
    camas = conjuntos["camas"]
    cirujanos = conjuntos["cirujanos"]
    anestesistas = conjuntos["anestesistas"]

    if model.status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and model.SolCount > 0:
        logger.info("=" * 60)
        logger.info("RESULTADOS")
        logger.info("=" * 60)
        logger.info(f"Valor funcion objetivo: {model.ObjVal:.4f}")
        logger.info("Pacientes programados:")

        cantidad_programados = 0
        for i in pacientes:
            if X[i].X > 0.5:
                cantidad_programados += 1
                for t in tiempos:
                    for p in pabellones:
                        if (i, t, p) in ZI and ZI[i, t, p].X > 0.5:
                            logger.info(f"Paciente {i} inicia cirugia en tiempo {t}, pabellon {p}")
                            for k in cirujanos:
                                if (i, t, p, k) in Y and Y[i, t, p, k].X > 0.5:
                                    logger.info(f"  Cirujano asignado: {k}")
                            for m in anestesistas:
                                if (i, t, p, m) in H and H[i, t, p, m].X > 0.5:
                                    logger.info(f"  Anestesista asignado: {m}")

        logger.info(f"\nTotal pacientes programados: {cantidad_programados}")
        logger.info("Uso de camas de recuperacion:")

        for i in pacientes:
            for t in tiempos:
                for c in camas:
                    if (i, t, c) in WI and WI[i, t, c].X > 0.5:
                        logger.info(f"Paciente {i} inicia recuperacion en tiempo {t}, cama {c}")
    else:
        logger.warning("No se encontro solucion factible u optima.")
        logger.warning(f"Estado del modelo: {model.status}")