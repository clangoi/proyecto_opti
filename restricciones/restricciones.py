# restricciones.py

import time

from .validaciones import validar_datos
from .restricciones_basicas import agregar_restricciones_basicas
from .restricciones_pabellones import agregar_restricciones_pabellones
from .restricciones_personal import agregar_restricciones_personal
from .restricciones_recuperacion import agregar_restricciones_recuperacion


def log_restricciones(mensaje: str) -> None:
    print(f"[restricciones] {mensaje}", flush=True)


def construir_ci_paciente(pacientes, cirugias, G):
    """
    Construye ci_paciente[i] = ci.

    Supuesto:
    Cada paciente tiene exactamente una cirugía:
    sum_ci G[i,ci] = 1
    """

    ci_paciente = {}

    for i in pacientes:
        cirugias_i = [
            ci
            for ci in cirugias
            if G[i, ci] == 1
        ]

        if len(cirugias_i) != 1:
            raise ValueError(
                f"Paciente {i} debe tener exactamente una cirugía. "
                f"Encontradas: {cirugias_i}"
            )

        ci_paciente[i] = cirugias_i[0]

    return ci_paciente


def construir_duracion_paciente(pacientes, ci_paciente, d, r):
    """
    Precalcula duración quirúrgica y recuperación por paciente.
    """

    duracion_qx_i = {
        i: int(d[ci_paciente[i]])
        for i in pacientes
    }

    duracion_rec_i = {
        i: int(r[ci_paciente[i]])
        for i in pacientes
    }

    duracion_total_i = {
        i: duracion_qx_i[i] + duracion_rec_i[i]
        for i in pacientes
    }

    return duracion_qx_i, duracion_rec_i, duracion_total_i


def resumen_variables(X, ZI, Z, LQ, WI, W, Y, H, O):
    """
    Imprime resumen de variables ya prefiltradas.
    """

    log_restricciones("Resumen de variables recibidas:")
    log_restricciones(f"  X : {len(X)}")
    log_restricciones(f"  ZI: {len(ZI)}")
    log_restricciones(f"  Z : {len(Z)}")
    log_restricciones(f"  LQ: {len(LQ)}")
    log_restricciones(f"  WI: {len(WI)}")
    log_restricciones(f"  W : {len(W)}")
    log_restricciones(f"  Y : {len(Y)}")
    log_restricciones(f"  H : {len(H)}")
    log_restricciones(f"  O : {len(O)}")


def agregar_restricciones(
    model,
    X,
    ZI,
    Z,
    LQ,
    WI,
    W,
    Y,
    H,
    O,
    pacientes,
    tiempos,
    pabellones,
    camas,
    cirujanos,
    anestesistas,
    cirugias,
    especialidades,
    G,
    E,
    A,
    Q,
    R,
    DispP,
    DispK,
    DispM,
    d,
    r,
    L,
    a,
    b,
    usar_update_final=True
):
    """
    Agrega todas las restricciones del modelo.

    Esta versión está pensada para variables prefiltradas:
    ZI, Z, LQ, WI, W, Y y H no necesariamente existen para todas
    las combinaciones.

    Estrategia:
    - Validar datos una vez.
    - Convertir conjuntos a listas.
    - Precalcular estructuras por paciente.
    - Usar módulos con addConstrs + quicksum + generadores.
    - Evitar model.update() entre bloques.
    """

    inicio = time.time()

    # ============================================================
    # 0. NORMALIZAR CONJUNTOS
    # ============================================================

    pacientes = list(pacientes)
    tiempos = list(tiempos)
    pabellones = list(pabellones)
    camas = list(camas)
    cirujanos = list(cirujanos)
    anestesistas = list(anestesistas)
    cirugias = list(cirugias)
    especialidades = list(especialidades)

    log_restricciones("Iniciando carga de restricciones")
    resumen_variables(X, ZI, Z, LQ, WI, W, Y, H, O)

    # ============================================================
    # 1. VALIDACIONES
    # ============================================================

    t0 = time.time()

    validar_datos(
        pacientes=pacientes,
        pabellones=pabellones,
        cirugias=cirugias,
        G=G,
        d=d,
        r=r,
        L=L
    )

    ci_paciente = construir_ci_paciente(
        pacientes=pacientes,
        cirugias=cirugias,
        G=G
    )

    duracion_qx_i, duracion_rec_i, duracion_total_i = construir_duracion_paciente(
        pacientes=pacientes,
        ci_paciente=ci_paciente,
        d=d,
        r=r
    )

    log_restricciones(f"Validaciones listas en {time.time() - t0:.2f} s")

    # ============================================================
    # 2. RESTRICCIONES BÁSICAS
    # ============================================================

    t0 = time.time()

    agregar_restricciones_basicas(
        model=model,
        X=X,
        ZI=ZI,
        pacientes=pacientes,
        tiempos=tiempos,
        pabellones=pabellones,
        cirugias=cirugias,
        especialidades=especialidades,
        G=G,
        E=E,
        A=A,
        a=a,
        b=b
    )

    log_restricciones(f"Restricciones básicas agregadas en {time.time() - t0:.2f} s")

    # ============================================================
    # 3. RESTRICCIONES DE PABELLONES
    # ============================================================

    t0 = time.time()

    agregar_restricciones_pabellones(
        model=model,
        ZI=ZI,
        Z=Z,
        LQ=LQ,
        O=O,
        pacientes=pacientes,
        tiempos=tiempos,
        pabellones=pabellones,
        cirugias=cirugias,
        G=G,
        d=d,
        r=r,
        L=L,
        DispP=DispP
    )

    log_restricciones(f"Restricciones de pabellones agregadas en {time.time() - t0:.2f} s")

    # ============================================================
    # 4. RESTRICCIONES DE PERSONAL
    # ============================================================

    t0 = time.time()

    agregar_restricciones_personal(
        model=model,
        ZI=ZI,
        Y=Y,
        H=H,
        pacientes=pacientes,
        tiempos=tiempos,
        pabellones=pabellones,
        cirujanos=cirujanos,
        anestesistas=anestesistas,
        cirugias=cirugias,
        G=G,
        Q=Q,
        R=R,
        d=d,
        DispK=DispK,
        DispM=DispM
    )

    log_restricciones(f"Restricciones de personal agregadas en {time.time() - t0:.2f} s")

    # ============================================================
    # 5. RESTRICCIONES DE RECUPERACIÓN
    # ============================================================

    t0 = time.time()

    agregar_restricciones_recuperacion(
        model=model,
        ZI=ZI,
        WI=WI,
        W=W,
        pacientes=pacientes,
        tiempos=tiempos,
        pabellones=pabellones,
        camas=camas,
        cirugias=cirugias,
        G=G,
        d=d,
        r=r
    )

    log_restricciones(f"Restricciones de recuperación agregadas en {time.time() - t0:.2f} s")

    # ============================================================
    # 6. UPDATE FINAL ÚNICO
    # ============================================================

    if usar_update_final:
        t0 = time.time()
        model.update()
        log_restricciones(f"model.update() final listo en {time.time() - t0:.2f} s")

    log_restricciones(f"Total restricciones agregadas: {model.NumConstrs}")
    log_restricciones(f"Tiempo total restricciones: {time.time() - inicio:.2f} s")

    return model