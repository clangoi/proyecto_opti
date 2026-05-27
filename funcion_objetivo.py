import gurobipy as gp
from gurobipy import GRB


def agregar_funcion_objetivo(
    model,
    X,
    O,
    pacientes,
    pabellones,
    tiempos,
    w,
    alpha
):
    # ============================================================
    # FUNCIÓN OBJETIVO
    # max sum_i w[i] X[i] - alpha sum_p sum_t O[p,t]
    # ============================================================

    model.setObjective(
        gp.quicksum(
            w[i] * X[i]
            for i in pacientes
        )
        -
        alpha * gp.quicksum(
            O[p, t]
            for p in pabellones
            for t in tiempos
        ),
        GRB.MAXIMIZE
    )

    return model