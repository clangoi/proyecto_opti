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
    # PREPROCESAMIENTO
    # ============================================================

    # Llaves existentes de ZI: solo combinaciones factibles creadas
    ZI_keys = list(ZI.keys())

    # ------------------------------------------------------------
    # Índice auxiliar:
    # ZI_por_paciente[i] = lista de variables ZI[i,t,p] existentes
    # ------------------------------------------------------------

    ZI_por_paciente = {i: [] for i in pacientes}

    for i, t, p in ZI_keys:
        ZI_por_paciente[i].append((i, t, p))

    # ------------------------------------------------------------
    # Compatibilidad paciente-pabellón:
    # compatibilidad_ip[i,p] = 1 si el pabellón p puede atender
    # la especialidad requerida por el paciente i.
    #
    # Se calcula como valor numérico, no como expresión Gurobi.
    # Esto ahorra memoria y restricciones.
    # ------------------------------------------------------------

    compatibilidad_ip = {}

    for i in pacientes:
        for p in pabellones:
            valor = sum(
                G[i, ci] * E[ci, s] * A[p, s]
                for ci in cirugias
                for s in especialidades
            )

            compatibilidad_ip[i, p] = int(valor)

    # ------------------------------------------------------------
    # Ventana temporal del paciente:
    # inicio_minimo_i = a[ci] de la cirugía asignada
    # inicio_maximo_i = b[ci] de la cirugía asignada
    # ------------------------------------------------------------

    ventana_i = {}

    for i in pacientes:
        inicio_minimo = sum(
            G[i, ci] * a[ci]
            for ci in cirugias
        )

        inicio_maximo = sum(
            G[i, ci] * b[ci]
            for ci in cirugias
        )

        ventana_i[i] = (
            int(inicio_minimo),
            int(inicio_maximo)
        )

    # ------------------------------------------------------------
    # Llaves ZI incompatibles por especialidad-pabellón.
    # Estas variables se fuerzan a 0.
    # ------------------------------------------------------------

    ZI_incompatibles = [
        (i, t, p)
        for i, t, p in ZI_keys
        if compatibilidad_ip[i, p] == 0
    ]

    # ------------------------------------------------------------
    # Llaves ZI fuera de ventana.
    # Estas variables se fuerzan a 0.
    # ------------------------------------------------------------

    ZI_fuera_ventana = [
        (i, t, p)
        for i, t, p in ZI_keys
        if (
            t < ventana_i[i][0]
            or t > ventana_i[i][1]
        )
    ]

    # ============================================================
    # 1. Un paciente solo puede ser operado si es programado
    #
    # sum_p sum_t ZI[i,t,p] = X[i]    para todo i
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                ZI[key]
                for key in ZI_por_paciente[i]
            ) == X[i]
            for i in pacientes
        ),
        name="R1_paciente_programado"
    )

    # ============================================================
    # 2. Compatibilidad especialidad-pabellón
    #
    # Si compatibilidad_ip[i,p] = 0, entonces ZI[i,t,p] = 0
    # para toda variable existente.
    #
    # Si compatibilidad_ip[i,p] = 1, no hace falta agregar restricción,
    # porque no restringe nada.
    # ============================================================

    model.addConstrs(
        (
            ZI[i, t, p] == 0
            for i, t, p in ZI_incompatibles
        ),
        name="R2_compatibilidad_especialidad_pabellon"
    )

    # ============================================================
    # 3. Ventana temporal
    #
    # Si t está fuera de [a[ci], b[ci]], entonces ZI[i,t,p] = 0.
    # Solo se agregan restricciones para variables ZI existentes.
    # ============================================================

    model.addConstrs(
        (
            ZI[i, t, p] == 0
            for i, t, p in ZI_fuera_ventana
        ),
        name="R3_ventana_temporal"
    )

    # ============================================================
    # INFORMACIÓN DE REDUCCIÓN
    # ============================================================

    print("[restricciones_basicas]")
    print(f"  ZI existentes: {len(ZI_keys)}")
    print(f"  R1 pacientes: {len(list(pacientes))}")
    print(f"  R2 incompatibles fijadas en 0: {len(ZI_incompatibles)}")
    print(f"  R3 fuera de ventana fijadas en 0: {len(ZI_fuera_ventana)}")

    return model