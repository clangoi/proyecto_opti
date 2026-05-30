import pandas as pd
from conjuntos import crear_conjuntos


def crear_parametros(data): 
# data  True para datos reales, False para datos sintéticos
    if not data:
        carpeta = "_sintetica/data/"
        sufijo = "_sint"
    else:    
        carpeta , sufijo = "/", ""
    pacientes, tiempos, pabellones, camas, cirujanos, anestesistas, cirugias, especialidades, tipos_cirugia = crear_conjuntos(data)

    # ============================================================
    # RUTAS DE ARCHIVOS CSV
    # ============================================================



    RUTA_PARAMETROS_CIRUGIA = f"data{carpeta}parametros_cirugia{sufijo}.csv"
    RUTA_LIMPIEZA_PABELLONES = f"data{carpeta}limpieza_pabellones{sufijo}.csv"
    RUTA_PRIORIDAD_PACIENTES = f"data{carpeta}prioridad_pacientes{sufijo}.csv"
    RUTA_ESPECIALIDAD_CIRUGIA = f"data{carpeta}especialidad_cirugia{sufijo}.csv"
    RUTA_CIRUJANO_CIRUGIA = f"data{carpeta}cirujano_cirugia{sufijo}.csv"
    RUTA_ANESTESISTA_CIRUGIA = f"data{carpeta}anestesista_cirugia{sufijo}.csv"
    RUTA_PABELLON_ESPECIALIDAD = f"data{carpeta}pabellon_especialidad{sufijo}.csv"
    RUTA_PACIENTE_CIRUGIA = f"data{carpeta}paciente_cirugia{sufijo}.csv"
    RUTA_DISP_PABELLONES = f"data{carpeta}disponibilidad_pabellones{sufijo}.csv"
    RUTA_DISP_CIRUJANOS = f"data{carpeta}disponibilidad_cirujanos{sufijo}.csv"
    RUTA_DISP_ANESTESISTAS = f"data{carpeta}disponibilidad_anestesistas{sufijo}.csv"


    # ============================================================
    # LECTURA DE CSV
    # ============================================================

    df_cirugia = pd.read_csv(RUTA_PARAMETROS_CIRUGIA, sep=";") # El CSV de parámetros de cirugía usa ; como separador
    df_limpieza = pd.read_csv(RUTA_LIMPIEZA_PABELLONES, sep=";")
    df_prioridad = pd.read_csv(RUTA_PRIORIDAD_PACIENTES, sep=";")
    df_E = pd.read_csv(RUTA_ESPECIALIDAD_CIRUGIA, sep=";")
    df_Q = pd.read_csv(RUTA_CIRUJANO_CIRUGIA, sep=";")
    df_R = pd.read_csv(RUTA_ANESTESISTA_CIRUGIA, sep=";")
    df_A = pd.read_csv(RUTA_PABELLON_ESPECIALIDAD, sep=";")
    df_G = pd.read_csv(RUTA_PACIENTE_CIRUGIA, sep=";")
    df_DispP = pd.read_csv(RUTA_DISP_PABELLONES, sep=";")
    df_DispK = pd.read_csv(RUTA_DISP_CIRUJANOS, sep=";")
    df_DispM = pd.read_csv(RUTA_DISP_ANESTESISTAS, sep=";")


    # ============================================================
    # PARÁMETROS ESCALARES
    # ============================================================

    alpha = 1 # Penalizacion por ociosidad


    # ============================================================
    # PARÁMETROS POR TIPO DE CIRUGÍA
    # CSV esperado:
    # ci,d,r,a,b
    # ============================================================

    d = {
        int(row["ci"]): float(row["d"])
        for _, row in df_cirugia.iterrows()
    }

    r = {
        int(row["ci"]): float(row["r"])
        for _, row in df_cirugia.iterrows()
    }

    a = {
        int(row["ci"]): int(row["a"])
        for _, row in df_cirugia.iterrows()
    }

    b = {
        int(row["ci"]): int(row["b"])
        for _, row in df_cirugia.iterrows()
    }


    # ============================================================
    # TIEMPO DE LIMPIEZA POR PABELLÓN
    # CSV esperado:
    # p,L
    # ============================================================

    L = {
        int(row["p"]): float(row["L"])
        for _, row in df_limpieza.iterrows()
    }


    # ============================================================
    # PRIORIDAD POR PACIENTE
    # CSV esperado:
    # i,w
    # ============================================================

    w = {
        int(row["i"]): float(row["w"])
        for _, row in df_prioridad.iterrows()
    }


    # ============================================================
    # E[ci,s] = 1 si cirugía ci requiere especialidad s
    # CSV esperado:
    # ci,s,valor
    # ============================================================

    E = {
        (ci, s): 0
        for i in pacientes
        for ci in tipos_cirugia[i]
        for s in especialidades
    }

    for _, row in df_E.iterrows():
        ci = int(row["ci"])
        s = int(row["s"])
        E[ci, s] = int(row["valor"])


    # ============================================================
    # Q[ci,k] = 1 si cirujano k puede operar cirugía tipo ci
    # CSV esperado:
    # ci,k,valor
    # ============================================================

    Q = {
        (ci, k): 0
        for i in pacientes
        for ci in tipos_cirugia[i]
        for k in cirujanos
    }

    for _, row in df_Q.iterrows():
        ci = int(row["ci"])
        k = int(row["k"])
        Q[ci, k] = int(row["valor"])


    # ============================================================
    # R[ci,m] = 1 si anestesista m puede asistir cirugía tipo ci
    # CSV esperado:
    # ci,m,valor
    # ============================================================

    R = {
        (ci, m): 0
        for i in pacientes
        for ci in tipos_cirugia[i]
        for m in anestesistas
    }

    for _, row in df_R.iterrows():
        ci = int(row["ci"])
        m = int(row["m"])
        R[ci, m] = int(row["valor"])


    # ============================================================
    # A[p,s] = 1 si pabellón p es compatible con especialidad s
    # CSV esperado:
    # p,s,valor
    # ============================================================

    A = {
        (p, s): 0
        for p in pabellones
        for s in especialidades
    }

    for _, row in df_A.iterrows():
        p = int(row["p"])
        s = int(row["s"])
        A[p, s] = int(row["valor"])


    # ============================================================
    # G[i,ci] = 1 si paciente i requiere cirugía tipo ci
    # CSV esperado:
    # i,ci,valor
    # ============================================================

    G = {
        (i, ci): 0
        for i in pacientes
        for ci in tipos_cirugia[i]
    }

    for _, row in df_G.iterrows():
        i = int(row["i"])
        ci = int(row["ci"])
        G[i, ci] = int(row["valor"])


    # ============================================================
    # DispP[p,t] = 1 si pabellón p está disponible en tiempo t
    # CSV esperado:
    # p,t,valor
    # ============================================================

    DispP = {
        (p, t): 1
        for p in pabellones
        for t in tiempos
    }

    for _, row in df_DispP.iterrows():
        p = int(row["p"])
        t = int(row["t"])
        DispP[p, t] = int(row["valor"])


    # ============================================================
    # DispK[k,t] = 1 si cirujano k está disponible en tiempo t
    # CSV esperado:
    # k,t,valor
    # ============================================================

    DispK = {
        (k, t): 1
        for k in cirujanos
        for t in tiempos
    }

    for _, row in df_DispK.iterrows():
        k = int(row["k"])
        t = int(row["t"])
        DispK[k, t] = int(row["valor"])


    # ============================================================
    # DispM[m,t] = 1 si anestesista m está disponible en tiempo t
    # CSV esperado:
    # m,t,valor
    # ============================================================

    DispM = {
        (m, t): 1
        for m in anestesistas
        for t in tiempos
    }

    for _, row in df_DispM.iterrows():
        m = int(row["m"])
        t = int(row["t"])
        DispM[m, t] = int(row["valor"])

    return alpha, d, r, a, b, L, w, E, Q, R, A, G, DispP, DispK, DispM