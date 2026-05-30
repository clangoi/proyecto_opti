# restricciones_personal.py

import gurobipy as gp
from collections import defaultdict


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
    # PREPROCESAMIENTO
    # ============================================================

    pacientes = list(pacientes)
    tiempos = list(tiempos)
    pabellones = list(pabellones)
    cirujanos = list(cirujanos)
    anestesistas = list(anestesistas)
    cirugias = list(cirugias)

    ZI_keys = list(ZI.keys())
    Y_keys = list(Y.keys())
    H_keys = list(H.keys())

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
    # Duración quirúrgica por paciente
    # ------------------------------------------------------------

    duracion_i = {
        i: int(d[ci_paciente[i]])
        for i in pacientes
        if i in ci_paciente
    }

    # ------------------------------------------------------------
    # Índices auxiliares para asignación
    # Y_por_inicio[i,t,p] = variables Y compatibles con ese inicio
    # H_por_inicio[i,t,p] = variables H compatibles con ese inicio
    # ------------------------------------------------------------

    Y_por_inicio = defaultdict(list)
    H_por_inicio = defaultdict(list)

    for i, t, p, k in Y_keys:
        Y_por_inicio[i, t, p].append((i, t, p, k))

    for i, t, p, m in H_keys:
        H_por_inicio[i, t, p].append((i, t, p, m))

    # ------------------------------------------------------------
    # Índices auxiliares para capacidad por bloque
    #
    # Y_ocupa_k_t[k,t] contiene todas las asignaciones Y que ocupan
    # al cirujano k durante el bloque t.
    #
    # H_ocupa_m_t[m,t] contiene todas las asignaciones H que ocupan
    # al anestesista m durante el bloque t.
    # ------------------------------------------------------------

    Y_ocupa_k_t = defaultdict(list)
    H_ocupa_m_t = defaultdict(list)

    for i, t_inicio, p, k in Y_keys:
        if i not in duracion_i:
            continue

        for tau in range(t_inicio, t_inicio + duracion_i[i]):
            if tau in tiempos:
                Y_ocupa_k_t[k, tau].append((i, t_inicio, p, k))

    for i, t_inicio, p, m in H_keys:
        if i not in duracion_i:
            continue

        for tau in range(t_inicio, t_inicio + duracion_i[i]):
            if tau in tiempos:
                H_ocupa_m_t[m, tau].append((i, t_inicio, p, m))

    # ------------------------------------------------------------
    # Variables incompatibles por seguridad.
    #
    # Si Y y H fueron creadas con prefiltrado, estas listas deberían
    # estar vacías o casi vacías. Se mantienen como validación.
    # ------------------------------------------------------------

    Y_incompatible = [
        (i, t, p, k)
        for i, t, p, k in Y_keys
        if i in ci_paciente and Q[ci_paciente[i], k] == 0
    ]

    H_incompatible = [
        (i, t, p, m)
        for i, t, p, m in H_keys
        if i in ci_paciente and R[ci_paciente[i], m] == 0
    ]

    # ------------------------------------------------------------
    # Variables que violan disponibilidad real.
    #
    # También deberían estar vacías si Y/H ya fueron prefiltradas
    # usando DispK_pos y DispM_pos.
    # ------------------------------------------------------------

    Y_no_disponible = []

    for i, t_inicio, p, k in Y_keys:
        if i not in duracion_i:
            continue

        for tau in range(t_inicio, t_inicio + duracion_i[i]):
            if tau in tiempos and DispK[k, tau] == 0:
                Y_no_disponible.append((i, t_inicio, p, k))
                break

    H_no_disponible = []

    for i, t_inicio, p, m in H_keys:
        if i not in duracion_i:
            continue

        for tau in range(t_inicio, t_inicio + duracion_i[i]):
            if tau in tiempos and DispM[m, tau] == 0:
                H_no_disponible.append((i, t_inicio, p, m))
                break

    # ============================================================
    # 7. Asignación de cirujano
    #
    # sum_k Y[i,t,p,k] = ZI[i,t,p]
    # Solo se agrega para ZI existentes.
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                Y[key]
                for key in Y_por_inicio[i, t, p]
            ) == ZI[i, t, p]
            for i, t, p in ZI_keys
        ),
        name="R7_asignacion_cirujano"
    )

    # ============================================================
    # 8. Capacidad de cirujanos
    #
    # Un cirujano no puede estar en más de una cirugía al mismo
    # tiempo.
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                Y[key]
                for key in Y_ocupa_k_t[k, t]
            ) <= 1
            for k in cirujanos
            for t in tiempos
        ),
        name="R8_capacidad_cirujano"
    )

    # ============================================================
    # 9. Compatibilidad de cirujano
    #
    # Si Q[ci,k] = 0, entonces Y[i,t,p,k] = 0.
    # Esta restricción es redundante si Y ya viene prefiltrada,
    # pero sirve como validación.
    # ============================================================

    model.addConstrs(
        (
            Y[i, t, p, k] == 0
            for i, t, p, k in Y_incompatible
        ),
        name="R9_compatibilidad_cirujano"
    )

    # ============================================================
    # 10. Asignación de anestesista
    #
    # sum_m H[i,t,p,m] = ZI[i,t,p]
    # Solo se agrega para ZI existentes.
    # ============================================================

    model.addConstrs(
        (
            gp.quicksum(
                H[key]
                for key in H_por_inicio[i, t, p]
            ) == ZI[i, t, p]
            for i, t, p in ZI_keys
        ),
        name="R10_asignacion_anestesista"
    )

    # ============================================================
    # 11. Capacidad de anestesistas
    #
    # Un anestesista no puede estar en más de una cirugía al mismo
    # tiempo.
    # ============================================================

    # model.addConstrs(
    #     (
    #         gp.quicksum(
    #             H[key]
    #             for key in H_ocupa_m_t[m, t]
    #         ) <= 1
    #         for m in anestesistas
    #         for t in tiempos
    #     ),
    #     name="R11_capacidad_anestesista"
    # )

    # ============================================================
    # 12. Compatibilidad de anestesista
    #
    # Si R[ci,m] = 0, entonces H[i,t,p,m] = 0.
    # Redundante si H ya viene prefiltrada, pero sirve como validación.
    # ============================================================

    model.addConstrs(
        (
            H[i, t, p, m] == 0
            for i, t, p, m in H_incompatible
        ),
        name="R12_compatibilidad_anestesista"
    )

    # ============================================================
    # 19. Disponibilidad real de cirujanos por turno
    #
    # Si DispK[k,tau] = 0 durante algún bloque de la cirugía,
    # entonces Y[i,t,p,k] = 0.
    # ============================================================

    model.addConstrs(
        (
            Y[i, t, p, k] == 0
            for i, t, p, k in Y_no_disponible
        ),
        name="R19_disponibilidad_real_cirujano"
    )

    # ============================================================
    # 20. Disponibilidad real de anestesistas por turno
    #
    # Si DispM[m,tau] = 0 durante algún bloque de la cirugía,
    # entonces H[i,t,p,m] = 0.
    # ============================================================

    model.addConstrs(
        (
            H[i, t, p, m] == 0
            for i, t, p, m in H_no_disponible
        ),
        name="R20_disponibilidad_real_anestesista"
    )

    # ============================================================
    # INFORMACIÓN DE REDUCCIÓN
    # ============================================================

    print("[restricciones_personal]")
    print(f"  ZI existentes: {len(ZI_keys)}")
    print(f"  Y existentes: {len(Y_keys)}")
    print(f"  H existentes: {len(H_keys)}")
    print(f"  Y incompatibles fijadas en 0: {len(Y_incompatible)}")
    print(f"  H incompatibles fijadas en 0: {len(H_incompatible)}")
    print(f"  Y no disponibles fijadas en 0: {len(Y_no_disponible)}")
    print(f"  H no disponibles fijadas en 0: {len(H_no_disponible)}")

    return model