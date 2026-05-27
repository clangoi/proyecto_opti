from gurobipy import GRB


def crear_variables(
    model,
    pacientes,
    tiempos,
    pabellones,
    camas,
    cirujanos,
    anestesistas
):
    # ============================================================
    # X[i] = 1 si el paciente i es operado
    # ============================================================

    X = model.addVars(
        pacientes,
        vtype=GRB.BINARY,
        name="X"
    )

    # ============================================================
    # ZI[i,t,p] = 1 si el paciente i inicia cirugía en pabellón p
    # en el tiempo t
    # ============================================================

    ZI = model.addVars(
        pacientes,
        tiempos,
        pabellones,
        vtype=GRB.BINARY,
        name="ZI"
    )

    # ============================================================
    # Z[i,t,p] = 1 si el paciente i ocupa el pabellón p
    # en el tiempo t
    # ============================================================

    Z = model.addVars(
        pacientes,
        tiempos,
        pabellones,
        vtype=GRB.BINARY,
        name="Z"
    )

    # ============================================================
    # LQ[i,t,p] = 1 si el pabellón p está en limpieza luego
    # de operar al paciente i en el tiempo t
    # ============================================================

    LQ = model.addVars(
        pacientes,
        tiempos,
        pabellones,
        vtype=GRB.BINARY,
        name="LQ"
    )

    # ============================================================
    # WI[i,t,c] = 1 si el paciente i entra a recuperación
    # en la cama c en el tiempo t
    # ============================================================

    WI = model.addVars(
        pacientes,
        tiempos,
        camas,
        vtype=GRB.BINARY,
        name="WI"
    )

    # ============================================================
    # W[i,t,c] = 1 si el paciente i ocupa la cama c
    # en el tiempo t
    # ============================================================

    W = model.addVars(
        pacientes,
        tiempos,
        camas,
        vtype=GRB.BINARY,
        name="W"
    )

    # ============================================================
    # Y[i,t,p,k] = 1 si el cirujano k es asignado a la cirugía
    # del paciente i en el pabellón p en el tiempo t
    # ============================================================

    Y = model.addVars(
        pacientes,
        tiempos,
        pabellones,
        cirujanos,
        vtype=GRB.BINARY,
        name="Y"
    )

    # ============================================================
    # H[i,t,p,m] = 1 si el anestesista m es asignado a la cirugía
    # del paciente i en el pabellón p en el tiempo t
    # ============================================================

    H = model.addVars(
        pacientes,
        tiempos,
        pabellones,
        anestesistas,
        vtype=GRB.BINARY,
        name="H"
    )

    # ============================================================
    # O[p,t] = 1 si el pabellón p está ocioso en el tiempo t
    # ============================================================

    O = model.addVars(
        pabellones,
        tiempos,
        vtype=GRB.BINARY,
        name="O"
    )

    return X, ZI, Z, LQ, WI, W, Y, H, O