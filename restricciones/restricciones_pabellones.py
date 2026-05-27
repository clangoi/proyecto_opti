# restricciones_pabellones.py

import gurobipy as gp


def agregar_restricciones_pabellones(
    model,
    ZI,
    Z,
    LQ,
    O,
    pacientes,
    tiempos,
    pabellones,
    cirugias,
    G,
    d,
    r,
    L,
    DispP
):
    # ============================================================
    # 4. Definición de ocupación del pabellón
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for p in pabellones:
                model.addConstr(
                    Z[i, t, p]
                    == gp.quicksum(
                        G[i, ci]
                        * gp.quicksum(
                            ZI[i, tau, p]
                            for tau in tiempos
                            if tau >= max(1, t - int(d[ci]) + 1) and tau <= t
                        )
                        for ci in cirugias
                    ),
                    name=f"R4_ocupacion_pabellon_{i}_{t}_{p}"
                )

    # ============================================================
    # 5. Definición de limpieza del pabellón
    # ============================================================

    for i in pacientes:
        for t in tiempos:
            for p in pabellones:
                model.addConstr(
                    LQ[i, t, p]
                    == gp.quicksum(
                        G[i, ci]
                        * gp.quicksum(
                            ZI[i, tau, p]
                            for tau in tiempos
                            if tau >= max(1, t - int(d[ci]) - int(L[p]) + 1)
                            and tau <= max(1, t - int(d[ci]))
                            and t > int(d[ci])
                        )
                        for ci in cirugias
                    ),
                    name=f"R5_limpieza_pabellon_{i}_{t}_{p}"
                )

    # ============================================================
    # 6. Capacidad del pabellón
    # ============================================================

    for p in pabellones:
        for t in tiempos:
            model.addConstr(
                gp.quicksum(Z[i, t, p] for i in pacientes)
                + gp.quicksum(LQ[i, t, p] for i in pacientes)
                <= 1,
                name=f"R6_capacidad_pabellon_{p}_{t}"
            )

    # ============================================================
    # 17. Definición de ociosidad del pabellón
    # ============================================================

    for p in pabellones:
        for t in tiempos:
            model.addConstr(
                O[p, t]
                <= DispP[p, t]
                - gp.quicksum(Z[i, t, p] for i in pacientes)
                - gp.quicksum(LQ[i, t, p] for i in pacientes),
                name=f"R17_ociosidad_pabellon_{p}_{t}"
            )

    # ============================================================
    # 17.2. Activación de ociosidad del pabellón
    # ============================================================

    for p in pabellones:
        for t in tiempos:
            model.addConstr(
                O[p, t]
                >= DispP[p, t]
                - gp.quicksum(Z[i, t, p] for i in pacientes)
                - gp.quicksum(LQ[i, t, p] for i in pacientes),
                name=f"R17b_activacion_ociosidad_pabellon_{p}_{t}"
            )

    # ============================================================
    # 18. Disponibilidad de pabellones
    # ============================================================

    for p in pabellones:
        for t in tiempos:
            model.addConstr(
                gp.quicksum(Z[i, t, p] for i in pacientes)
                + gp.quicksum(LQ[i, t, p] for i in pacientes)
                <= DispP[p, t],
                name=f"R18_disponibilidad_pabellon_{p}_{t}"
            )

    # ============================================================
    # 21. Límite horizonte dado por cirugía más recuperación
    # ============================================================

    T_max = max(tiempos)

    for i in pacientes:
        duracion_total_i = sum(G[i, ci] * (d[ci] + r[ci]) for ci in cirugias)

        for t in tiempos:
            for p in pabellones:
                if t + duracion_total_i - 1 > T_max:
                    model.addConstr(
                        ZI[i, t, p] == 0,
                        name=f"R21_limite_horizonte_{i}_{t}_{p}"
                    )

    return model
