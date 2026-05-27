# validaciones.py


def validar_datos(pacientes, pabellones, cirugias, G, d, r, L):
    # ============================================================
    # 0.1. Validación: cada paciente debe tener exactamente una cirugía
    # ============================================================

    for i in pacientes:
        if sum(G[i, ci] for ci in cirugias) != 1:
            raise ValueError(
                f"El paciente {i} debe tener exactamente una cirugía asignada en G."
            )

    # ============================================================
    # 0.2. Validación: duraciones deben ser enteras positivas
    # ============================================================

    for ci in cirugias:
        if int(d[ci]) != d[ci] or d[ci] <= 0:
            raise ValueError(f"La duración d[{ci}] debe ser entera positiva.")

        if int(r[ci]) != r[ci] or r[ci] <= 0:
            raise ValueError(f"La recuperación r[{ci}] debe ser entera positiva.")

    for p in pabellones:
        if int(L[p]) != L[p] or L[p] < 0:
            raise ValueError(f"El tiempo de limpieza L[{p}] debe ser entero no negativo.")
