# restricciones_pabellones.py

import gurobipy as gp
from collections import defaultdict


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
    # PREPROCESAMIENTO
    # ============================================================

    tiempos = list(tiempos)
    pabellones = list(pabellones)
    pacientes = list(pacientes)
    cirugias = list(cirugias)

    T_max = max(tiempos)

    ZI_keys = list(ZI.keys())
    Z_keys = list(Z.keys())
    LQ_keys = list(LQ.keys())

    # ------------------------------------------------------------
    # Cirugía asignada a cada paciente
    # Como G[i,ci] = 1 para exactamente una cirugía por paciente
    # ------------------------------------------------------------

    ci_paciente = {}

    for i in pacientes:
        for ci in cirugias:
            if G[i, ci] == 1:
                ci_paciente[i] = ci
                break

    # ------------------------------------------------------------
    # Duraciones por paciente
    # ------------------------------------------------------------

    duracion_qx_i = {
        i: int(d[ci_paciente[i]])
        for i in pacientes
        if i in ci_paciente
    }

    duracion_total_i = {
        i: int(d[ci_paciente[i]] + r[ci_paciente[i]])
        for i in pacientes
        if i in ci_paciente
    }

    # ------------------------------------------------------------
    # Índices auxiliares para evitar recorrer combinaciones completas
    # ------------------------------------------------------------

    Z_por_pabellon_t = defaultdict(list)
    LQ_por_pabellon_t = defaultdict(list)

    for i, t, p in Z_keys:
        Z_por_pabellon_t[p, t].append((i, t, p))

    for i, t, p in LQ_keys:
        LQ_por_pabellon_t[p, t].append((i, t, p))

    # ------------------------------------------------------------
    # Para definir Z[i,t,p], buscamos los inicios ZI[i,tau,p]
    # que cubren el bloque t.
    # ------------------------------------------------------------

    ZI_cubre_Z = defaultdict(list)

    for i, tau, p in ZI_keys:
        if i not in duracion_qx_i:
            continue

        duracion = duracion_qx_i[i]

        for t in range(tau, tau + duracion):
            if t <= T_max and (i, t, p) in Z:
                ZI_cubre_Z[i, t, p].append((i, tau, p))

    # ------------------------------------------------------------
    # Para definir LQ[i,t,p], buscamos los inicios ZI[i,tau,p]
    # que generan limpieza en el bloque t.
    # ------------------------------------------------------------

    ZI_genera_LQ = defaultdict(list)

    for i, tau, p in ZI_keys:
        if i not in duracion_qx_i:
            continue

        duracion = duracion_qx_i[i]
        limpieza_p = int(L[p])

        inicio_limpieza = tau + duracion
        fin_limpieza = tau + duracion + limpieza_p - 1

        for t in range(inicio_limpieza, fin_limpieza + 1):
            if t <= T_max and (i, t, p) in LQ:
                ZI_genera_LQ[i, t, p].append((i, tau, p))

    # ------------------------------------------------------------
    # Variables ZI fuera del horizonte cirugía + recuperación.
    # ------------------------------------------------------------

    ZI_fuera_horizonte = [
        (i, t, p)
        for i, t, p in ZI_keys
        if i in duracion_total_i
        and t + duracion_total_i[i] - 1 > T_max
    ]

    # ============================================================
    # 4. Definición de ocupación del pabellón
    #
    # Z[i,t,p] = sum de inicios ZI que cubren ese bloque.
    # ============================================================

    model.addConstrs(
        (
            Z[i, t, p]
            ==
            gp.quicksum(
                ZI[key]
                for key in ZI_cubre_Z[i, t, p]
            )
            for i, t, p in Z_keys
        ),
        name="R4_ocupacion_pabellon"
    )

    # ============================================================
    # 5. Definición de limpieza del pabellón
    #
    # LQ[i,t,p] = sum de inicios ZI que generan limpieza en t.
    # ============================================================

    model.addConstrs(
        (
            LQ[i, t, p]
            ==
            gp.quicksum(
                ZI[key]
                for key in ZI_genera_LQ[i, t, p]
            )
            for i, t, p in LQ_keys
        ),
        name="R5_limpieza_pabellon"
    )

    # ============================================================
    # 6. Capacidad del pabellón
    #
    # Ocupación + limpieza <= 1
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                Z[key]
                for key in Z_por_pabellon_t[p, t]
            )
            +
            gp.quicksum(
                LQ[key]
                for key in LQ_por_pabellon_t[p, t]
            )
            <= 1
            for p in pabellones
            for t in tiempos
        ),
        name="R6_capacidad_pabellon"
    )

    # ============================================================
    # 17. Definición de ociosidad del pabellón
    #
    # O[p,t] <= DispP[p,t] - ocupación - limpieza
    # ============================================================

    model.addConstrs(
        (
            O[p, t]
            <=
            DispP[p, t]
            -
            gp.quicksum(
                Z[key]
                for key in Z_por_pabellon_t[p, t]
            )
            -
            gp.quicksum(
                LQ[key]
                for key in LQ_por_pabellon_t[p, t]
            )
            for p in pabellones
            for t in tiempos
        ),
        name="R17_ociosidad_pabellon"
    )

    # ============================================================
    # 17.2. Activación de ociosidad del pabellón
    #
    # O[p,t] >= DispP[p,t] - ocupación - limpieza
    # ============================================================

    model.addConstrs(
        (
            O[p, t]
            >=
            DispP[p, t]
            -
            gp.quicksum(
                Z[key]
                for key in Z_por_pabellon_t[p, t]
            )
            -
            gp.quicksum(
                LQ[key]
                for key in LQ_por_pabellon_t[p, t]
            )
            for p in pabellones
            for t in tiempos
        ),
        name="R17b_activacion_ociosidad_pabellon"
    )

    # ============================================================
    # 18. Disponibilidad de pabellones
    #
    # Ocupación + limpieza <= DispP[p,t]
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                Z[key]
                for key in Z_por_pabellon_t[p, t]
            )
            +
            gp.quicksum(
                LQ[key]
                for key in LQ_por_pabellon_t[p, t]
            )
            <= DispP[p, t]
            for p in pabellones
            for t in tiempos
        ),
        name="R18_disponibilidad_pabellon"
    )

    # ============================================================
    # 21. Límite horizonte dado por cirugía + recuperación
    #
    # Si no cabe cirugía + recuperación, se fuerza ZI = 0.
    # ============================================================

    model.addConstrs(
        (
            ZI[i, t, p] == 0
            for i, t, p in ZI_fuera_horizonte
        ),
        name="R21_limite_horizonte"
    )

    # ============================================================
    # INFORMACIÓN DE REDUCCIÓN
    # ============================================================

    print("[restricciones_pabellones]")
    print(f"  ZI existentes: {len(ZI_keys)}")
    print(f"  Z existentes: {len(Z_keys)}")
    print(f"  LQ existentes: {len(LQ_keys)}")
    print(f"  R21 fuera de horizonte fijadas en 0: {len(ZI_fuera_horizonte)}")

    return model