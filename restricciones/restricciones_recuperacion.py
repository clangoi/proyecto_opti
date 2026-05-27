# restricciones_recuperacion.py

import gurobipy as gp


def agregar_restricciones_recuperacion(
    model,
    ZI,
    WI,
    W,
    pacientes,
    tiempos,
    pabellones,
    camas,
    cirugias,
    G,
    d,
    r
):
    # ============================================================
    # 13. Inicio de recuperación posterior a cirugía
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            model.addConstr(
                gp.quicksum(WI[i, t, c] for c in camas)
                == gp.quicksum(
                    G[i, ci]
                    * gp.quicksum(
                        ZI[i, t - int(d[ci]), p]
                        for p in pabellones
                        if (t - int(d[ci])) in tiempos
                    )
                    for ci in cirugias
                ),
                name=f"R13_inicio_recuperacion_{i}_{t}"
            )

    # ============================================================
    # 14. Definición de ocupación de camas
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for c in camas:
                model.addConstr(
                    W[i, t, c]
                    == gp.quicksum(
                        G[i, ci]
                        * gp.quicksum(
                            WI[i, tau, c]
                            for tau in tiempos
                            if tau >= max(1, t - int(r[ci]) + 1)
                            and tau <= t
                        )
                        for ci in cirugias
                    ),
                    name=f"R14_ocupacion_camas_{i}_{t}_{c}"
                )

    # ============================================================
    # 15. Capacidad de camas de recuperación
    # ============================================================

    for c in camas:
        for t in tiempos:
            model.addConstr(
                gp.quicksum(W[i, t, c] for i in pacientes) <= 1,
                name=f"R15_capacidad_cama_{c}_{t}"
            )

    # ============================================================
    # 16. Un paciente no puede ocupar más de una cama
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            model.addConstr(
                gp.quicksum(W[i, t, c] for c in camas) <= 1,
                name=f"R16_paciente_una_cama_{i}_{t}"
            )

    return model
