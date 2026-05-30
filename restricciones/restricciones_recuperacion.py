# restricciones_recuperacion.py

import gurobipy as gp
from collections import defaultdict


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
    # PREPROCESAMIENTO
    # ============================================================

    pacientes = list(pacientes)
    tiempos = list(tiempos)
    pabellones = list(pabellones)
    camas = list(camas)
    cirugias = list(cirugias)

    ZI_keys = list(ZI.keys())
    WI_keys = list(WI.keys())
    W_keys = list(W.keys())

    tiempo_set = set(tiempos)

    # ------------------------------------------------------------
    # Cirugía asignada a cada paciente
    # G[i,ci] = 1 para exactamente una cirugía
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

    duracion_rec_i = {
        i: int(r[ci_paciente[i]])
        for i in pacientes
        if i in ci_paciente
    }

    # ------------------------------------------------------------
    # WI_por_paciente_t[i,t] = variables WI[i,t,c] existentes
    # ------------------------------------------------------------

    WI_por_paciente_t = defaultdict(list)

    for i, t, c in WI_keys:
        WI_por_paciente_t[i, t].append((i, t, c))

    # ------------------------------------------------------------
    # ZI_termina_en[i,t] = variables ZI[i,t_inicio,p] que terminan
    # cirugía justo en t.
    #
    # Si la cirugía inicia en tau y dura d_i, entonces recuperación
    # inicia en t = tau + d_i.
    # ------------------------------------------------------------

    ZI_termina_en = defaultdict(list)

    for i, tau, p in ZI_keys:
        if i not in duracion_qx_i:
            continue

        t_rec = tau + duracion_qx_i[i]

        if t_rec in tiempo_set:
            ZI_termina_en[i, t_rec].append((i, tau, p))

    # ------------------------------------------------------------
    # WI_cubre_W[i,t,c] = variables WI[i,tau,c] que hacen que el
    # paciente i ocupe cama c durante el bloque t.
    #
    # Si recuperación inicia en tau y dura r_i, entonces ocupa:
    # tau, tau+1, ..., tau+r_i-1.
    # ------------------------------------------------------------

    WI_cubre_W = defaultdict(list)

    for i, tau, c in WI_keys:
        if i not in duracion_rec_i:
            continue

        for t in range(tau, tau + duracion_rec_i[i]):
            if t in tiempo_set and (i, t, c) in W:
                WI_cubre_W[i, t, c].append((i, tau, c))

    # ------------------------------------------------------------
    # W_por_cama_t[c,t] = variables W[i,t,c] existentes
    # W_por_paciente_t[i,t] = variables W[i,t,c] existentes
    # ------------------------------------------------------------

    W_por_cama_t = defaultdict(list)
    W_por_paciente_t = defaultdict(list)

    for i, t, c in W_keys:
        W_por_cama_t[c, t].append((i, t, c))
        W_por_paciente_t[i, t].append((i, t, c))

    # ============================================================
    # 13. Inicio de recuperación posterior a cirugía
    #
    # sum_c WI[i,t,c] = sum_p ZI[i,t-d_i,p]
    #
    # Solo se usan variables existentes.
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                WI[key]
                for key in WI_por_paciente_t[i, t]
            )
            ==
            gp.quicksum(
                ZI[key]
                for key in ZI_termina_en[i, t]
            )
            for i in pacientes
            for t in tiempos
        ),
        name="R13_inicio_recuperacion"
    )

    # ============================================================
    # 14. Definición de ocupación de camas
    #
    # W[i,t,c] = sum de inicios WI que cubren ese bloque.
    # ============================================================

    model.addConstrs(
        (
            W[i, t, c]
            ==
            gp.quicksum(
                WI[key]
                for key in WI_cubre_W[i, t, c]
            )
            for i, t, c in W_keys
        ),
        name="R14_ocupacion_camas"
    )

    # ============================================================
    # 15. Capacidad de camas de recuperación
    #
    # Una cama puede tener a lo más un paciente en cada tiempo.
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                W[key]
                for key in W_por_cama_t[c, t]
            ) <= 1
            for c in camas
            for t in tiempos
        ),
        name="R15_capacidad_cama"
    )

    # ============================================================
    # 16. Un paciente no puede ocupar más de una cama
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                W[key]
                for key in W_por_paciente_t[i, t]
            ) <= 1
            for i in pacientes
            for t in tiempos
        ),
        name="R16_paciente_una_cama"
    )

    # ============================================================
    # INFORMACIÓN DE REDUCCIÓN
    # ============================================================

    print("[restricciones_recuperacion]")
    print(f"  ZI existentes: {len(ZI_keys)}")
    print(f"  WI existentes: {len(WI_keys)}")
    print(f"  W existentes: {len(W_keys)}")
    print(f"  Pares WI_por_paciente_t: {len(WI_por_paciente_t)}")
    print(f"  Pares ZI_termina_en: {len(ZI_termina_en)}")
    print(f"  Pares W_por_cama_t: {len(W_por_cama_t)}")
    print(f"  Pares W_por_paciente_t: {len(W_por_paciente_t)}")

    return model