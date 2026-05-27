# restricciones_basicas.py

import gurobipy as gp


def agregar_restricciones_basicas(
    model,
    X,
    ZI,
    pacientes,
    tiempos,
    pabellones,
    cirugias,
    especialidades,
    G,
    E,
    A,
    a,
    b
):
    # ============================================================
    # 1. Un paciente solo puede ser operado si es programado
    # sum_p sum_t ZI[i,t,p] = X[i]    para todo i
    # ============================================================

    for i in pacientes:
        model.addConstr(
            gp.quicksum(
                ZI[i, t, p]
                for p in pabellones
                for t in tiempos
            ) == X[i],
            name=f"R1_paciente_programado_{i}"
        )

    # ============================================================
    # 2. Compatibilidad especialidad-pabellón
    # ZI[i,t,p] <= sum_ci sum_s G[i,ci] * E[ci,s] * A[p,s]
    # para todo i,t,p
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for p in pabellones:
                model.addConstr(
                    ZI[i, t, p]
                    <= gp.quicksum(
                        G[i, ci] * E[ci, s] * A[p, s]
                        for ci in cirugias
                        for s in especialidades
                    ),
                    name=f"R2_compatibilidad_especialidad_pabellon_{i}_{t}_{p}"
                )

    # ============================================================
    # 3. Ventana temporal
    # ZI[i,t,p] = 0 si t < sum_ci G[i,ci] * a[ci]
    # o si t > sum_ci G[i,ci] * b[ci]
    # para todo i,p,t
    # ============================================================

    for i in pacientes:
        inicio_minimo = sum(G[i, ci] * a[ci] for ci in cirugias)
        inicio_maximo = sum(G[i, ci] * b[ci] for ci in cirugias)

        for p in pabellones:
            for t in tiempos:
                if t < inicio_minimo or t > inicio_maximo:
                    model.addConstr(
                        ZI[i, t, p] == 0,
                        name=f"R3_ventana_temporal_{i}_{t}_{p}"
                    )

    return model
