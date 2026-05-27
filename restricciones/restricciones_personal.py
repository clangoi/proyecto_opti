# restricciones_personal.py

import gurobipy as gp


def agregar_restricciones_personal(
    model,
    ZI,
    Y,
    H,
    pacientes,
    tiempos,
    pabellones,
    cirujanos,
    anestesistas,
    cirugias,
    G,
    Q,
    R,
    d,
    DispK,
    DispM
):
    # ============================================================
    # 7. Asignación de cirujano
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for p in pabellones:
                model.addConstr(
                    gp.quicksum(Y[i, t, p, k] for k in cirujanos)
                    == ZI[i, t, p],
                    name=f"R7_asignacion_cirujano_{i}_{t}_{p}"
                )

    # ============================================================
    # 8. Disponibilidad de cirujanos
    # ============================================================

    for k in cirujanos:
        for t in tiempos:
            model.addConstr(
                gp.quicksum(
                    G[i, ci]
                    * gp.quicksum(
                        Y[i, tau, p, k]
                        for tau in tiempos
                        if tau >= max(1, t - int(d[ci]) + 1)
                        and tau <= t
                    )
                    for i in pacientes
                    for p in pabellones
                    for ci in cirugias
                )
                <= 1,
                name=f"R8_disponibilidad_cirujano_{k}_{t}"
            )

    # ============================================================
    # 9. Compatibilidad de cirujano
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for p in pabellones:
                for k in cirujanos:
                    model.addConstr(
                        Y[i, t, p, k]
                        <= gp.quicksum(G[i, ci] * Q[ci, k] for ci in cirugias),
                        name=f"R9_compatibilidad_cirujano_{i}_{t}_{p}_{k}"
                    )

    # ============================================================
    # 10. Asignación de anestesista
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for p in pabellones:
                model.addConstr(
                    gp.quicksum(H[i, t, p, m] for m in anestesistas)
                    == ZI[i, t, p],
                    name=f"R10_asignacion_anestesista_{i}_{t}_{p}"
                )

    # ============================================================
    # 11. Disponibilidad de anestesistas
    # ============================================================

    for m in anestesistas:
        for t in tiempos:
            model.addConstr(
                gp.quicksum(
                    G[i, ci]
                    * gp.quicksum(
                        H[i, tau, p, m]
                        for tau in tiempos
                        if tau >= max(1, t - int(d[ci]) + 1)
                        and tau <= t
                    )
                    for i in pacientes
                    for p in pabellones
                    for ci in cirugias
                )
                <= 1,
                name=f"R11_disponibilidad_anestesista_{m}_{t}"
            )

    # ============================================================
    # 12. Compatibilidad de anestesista
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for p in pabellones:
                for m in anestesistas:
                    model.addConstr(
                        H[i, t, p, m]
                        <= gp.quicksum(G[i, ci] * R[ci, m] for ci in cirugias),
                        name=f"R12_compatibilidad_anestesista_{i}_{t}_{p}_{m}"
                    )

    # ============================================================
    # 19. Disponibilidad real de cirujanos por turno
    # ============================================================

    for i in pacientes:
        duracion_i = int(sum(G[i, ci] * d[ci] for ci in cirugias))

        for t in tiempos:
            for p in pabellones:
                for k in cirujanos:
                    for tau in tiempos:
                        if tau >= t and tau <= t + duracion_i - 1:
                            model.addConstr(
                                Y[i, t, p, k] <= DispK[k, tau],
                                name=f"R19_disponibilidad_real_cirujano_{i}_{t}_{p}_{k}_{tau}"
                            )

    # ============================================================
    # 20. Disponibilidad real de anestesistas por turno
    # ============================================================

    for i in pacientes:
        duracion_i = int(sum(G[i, ci] * d[ci] for ci in cirugias))

        for t in tiempos:
            for p in pabellones:
                for m in anestesistas:
                    for tau in tiempos:
                        if tau >= t and tau <= t + duracion_i - 1:
                            model.addConstr(
                                H[i, t, p, m] <= DispM[m, tau],
                                name=f"R20_disponibilidad_real_anestesista_{i}_{t}_{p}_{m}_{tau}"
                            )

    return model
