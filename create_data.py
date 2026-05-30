import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

np.random.seed(42)

def crear_data(data):
    if data:
        DATA_DIR = Path("data")
        # TODO
        # Falta agregar estructura para cuando estén los datos reales
        return
    else:
        DATA_DIR = Path("data_sintetica/data")
        DATA_DIR.mkdir(exist_ok=True)

    # Cantidad de datos sintéticos
    I = 3000   # Pacientes
    T = 18    # Bloques horarios
    P = 13     # Pabellones
    C = 26     # Camas de recuperación
    K = 23     # Cirujanos
    M = 4     # Anestesistas
    S = 19     # Especialidades
    CI = 24    # Tipos de cirugía

    # Separador de salida
    SEP = ";"

    # ============================================================
    # 1. PARÁMETROS GLOBALES
    # CSV esperado: parametro;valor
    # ============================================================

    df_globales = pd.DataFrame({
        "parametro": ["I", "T", "P", "C", "K", "M", "S", "CI"],
        "valor": [I, T, P, C, K, M, S, CI]
    })

    df_globales.to_csv(DATA_DIR / "parametros_globales_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 2. PARÁMETROS DE CIRUGÍA
    # CSV esperado: ci;d;r;a;b
    #
    # d: duración cirugía
    # r: duración recuperación
    # a: inicio mínimo permitido
    # b: inicio máximo permitido
    # ============================================================

    d = {}
    r = {}
    a = {}
    b = {}

    for ci in range(1, CI + 1):
        d[ci] = int(np.random.randint(2, 6))   # 2 a 5 bloques
        r[ci] = int(np.random.randint(1, 5))   # 1 a 4 bloques

        # Último inicio factible para que cirugía + recuperación quepan en el horizonte
        ultimo_inicio_factible = T - d[ci] - r[ci] + 1

        if ultimo_inicio_factible < 1:
            raise ValueError(
                f"La cirugía {ci} no cabe en el horizonte: "
                f"T={T}, d={d[ci]}, r={r[ci]}"
            )

        # Inicio mínimo factible
        a_min = 1
        a_max = min(8, ultimo_inicio_factible)

        a[ci] = int(np.random.randint(a_min, a_max + 1))

        # Inicio máximo factible
        b_min = a[ci]
        b_max = ultimo_inicio_factible

        b[ci] = int(np.random.randint(b_min, b_max + 1))

    df_cirugias = pd.DataFrame({
        "ci": list(range(1, CI + 1)),
        "d": [d[ci] for ci in range(1, CI + 1)],
        "r": [r[ci] for ci in range(1, CI + 1)],
        "a": [a[ci] for ci in range(1, CI + 1)],
        "b": [b[ci] for ci in range(1, CI + 1)],
    })

    df_cirugias.to_csv(DATA_DIR / "parametros_cirugia_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 3. LIMPIEZA DE PABELLONES
    # CSV esperado: p;L
    # ============================================================

    L = {
        p: int(np.random.randint(0, 3))  # 0 a 2 bloques
        for p in range(1, P + 1)
    }

    df_limpieza = pd.DataFrame({
        "p": list(range(1, P + 1)),
        "L": [L[p] for p in range(1, P + 1)],
    })

    df_limpieza.to_csv(DATA_DIR / "limpieza_pabellones_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 4. PRIORIDAD DE PACIENTES
    # CSV esperado: i;w
    # ============================================================

    w = {
        i: int(np.random.randint(1, 11))  # 1 a 10
        for i in range(1, I + 1)
    }

    df_prioridad = pd.DataFrame({
        "i": list(range(1, I + 1)),
        "w": [w[i] for i in range(1, I + 1)],
    })

    df_prioridad.to_csv(DATA_DIR / "prioridad_pacientes_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 5. ESPECIALIDAD REQUERIDA POR CIRUGÍA
    # E[ci,s] = 1 si cirugía ci requiere especialidad s
    # CSV esperado: ci;s;valor
    # ============================================================

    E = {}

    for ci in range(1, CI + 1):
        especialidades_ci = np.random.choice(
            range(1, S + 1),
            size=int(np.random.randint(1, min(3, S + 1))),
            replace=False
        )

        for s in range(1, S + 1):
            E[(ci, s)] = 1 if s in especialidades_ci else 0

    df_E = pd.DataFrame({
        "ci": [ci for ci in range(1, CI + 1) for s in range(1, S + 1)],
        "s": [s for ci in range(1, CI + 1) for s in range(1, S + 1)],
        "valor": [E[(ci, s)] for ci in range(1, CI + 1) for s in range(1, S + 1)],
    })

    df_E.to_csv(DATA_DIR / "especialidad_cirugia_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 6. COMPATIBILIDAD CIRUJANO-CIRUGÍA
    # Q[ci,k] = 1 si cirujano k puede operar cirugía ci
    # CSV esperado: ci;k;valor
    # ============================================================

    Q = {}

    for ci in range(1, CI + 1):
        cirujanos_ci = np.random.choice(
            range(1, K + 1),
            size=min(3, K),
            replace=False
        )

        for k in range(1, K + 1):
            Q[(ci, k)] = 1 if k in cirujanos_ci else 0

    df_Q = pd.DataFrame({
        "ci": [ci for ci in range(1, CI + 1) for k in range(1, K + 1)],
        "k": [k for ci in range(1, CI + 1) for k in range(1, K + 1)],
        "valor": [Q[(ci, k)] for ci in range(1, CI + 1) for k in range(1, K + 1)],
    })

    df_Q.to_csv(DATA_DIR / "cirujano_cirugia_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 7. COMPATIBILIDAD ANESTESISTA-CIRUGÍA
    # R[ci,m] = 1 si anestesista m puede asistir cirugía ci
    # CSV esperado: ci;m;valor
    # ============================================================

    R = {}

    for ci in range(1, CI + 1):
        anestesistas_ci = np.random.choice(
            range(1, M + 1),
            size=min(2, M),
            replace=False
        )

        for m in range(1, M + 1):
            R[(ci, m)] = 1 if m in anestesistas_ci else 0

    df_R = pd.DataFrame({
        "ci": [ci for ci in range(1, CI + 1) for m in range(1, M + 1)],
        "m": [m for ci in range(1, CI + 1) for m in range(1, M + 1)],
        "valor": [R[(ci, m)] for ci in range(1, CI + 1) for m in range(1, M + 1)],
    })

    df_R.to_csv(DATA_DIR / "anestesista_cirugia_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 8. COMPATIBILIDAD PABELLÓN-ESPECIALIDAD
    # A[p,s] = 1 si pabellón p es compatible con especialidad s
    # CSV esperado: p;s;valor
    # ============================================================

    A = {(p, s): 0 for p in range(1, P + 1) for s in range(1, S + 1)}

    for s in range(1, S + 1):
        pabellones_s = np.random.choice(
            range(1, P + 1),
            size=min(2, P),
            replace=False
        )

        for p in pabellones_s:
            A[(p, s)] = 1

    # Compatibilidades adicionales
    for p in range(1, P + 1):
        for s in range(1, S + 1):
            if np.random.rand() < 0.25:
                A[(p, s)] = 1

    df_A = pd.DataFrame({
        "p": [p for p in range(1, P + 1) for s in range(1, S + 1)],
        "s": [s for p in range(1, P + 1) for s in range(1, S + 1)],
        "valor": [A[(p, s)] for p in range(1, P + 1) for s in range(1, S + 1)],
    })

    df_A.to_csv(DATA_DIR / "pabellon_especialidad_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 9. PACIENTE-CIRUGÍA
    # G[i,ci] = 1 si paciente i requiere cirugía ci
    # CSV esperado: i;ci;valor
    #
    # REGLA:
    # Cada paciente debe tener exactamente una cirugía.
    # ============================================================

    G = {}

    for i in range(1, I + 1):
        ci_asignada = int(np.random.randint(1, CI + 1))

        for ci in range(1, CI + 1):
            G[(i, ci)] = 1 if ci == ci_asignada else 0

    df_G = pd.DataFrame({
        "i": [i for i in range(1, I + 1) for ci in range(1, CI + 1)],
        "ci": [ci for i in range(1, I + 1) for ci in range(1, CI + 1)],
        "valor": [G[(i, ci)] for i in range(1, I + 1) for ci in range(1, CI + 1)],
    })

    validacion_G = df_G.groupby("i")["valor"].sum()
    assert (validacion_G == 1).all(), "Error: hay pacientes con cero o más de una cirugía."

    df_G.to_csv(DATA_DIR / "paciente_cirugia_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 10. DISPONIBILIDAD DE PABELLONES
    # DispP[p,t] = 1 si pabellón p está disponible en tiempo t
    # CSV esperado: p;t;valor
    # ============================================================

    DispP = {}

    for p in range(1, P + 1):
        for t in range(1, T + 1):
            DispP[(p, t)] = 1 if np.random.rand() < 0.90 else 0

    df_DispP = pd.DataFrame({
        "p": [p for p in range(1, P + 1) for t in range(1, T + 1)],
        "t": [t for p in range(1, P + 1) for t in range(1, T + 1)],
        "valor": [DispP[(p, t)] for p in range(1, P + 1) for t in range(1, T + 1)],
    })

    df_DispP.to_csv(DATA_DIR / "disponibilidad_pabellones_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 11. DISPONIBILIDAD DE CIRUJANOS
    # DispK[k,t] = 1 si cirujano k está disponible en tiempo t
    # CSV esperado: k;t;valor
    # ============================================================

    DispK = {}

    for k in range(1, K + 1):
        for t in range(1, T + 1):
            DispK[(k, t)] = 1 if np.random.rand() < 0.85 else 0

    df_DispK = pd.DataFrame({
        "k": [k for k in range(1, K + 1) for t in range(1, T + 1)],
        "t": [t for k in range(1, K + 1) for t in range(1, T + 1)],
        "valor": [DispK[(k, t)] for k in range(1, K + 1) for t in range(1, T + 1)],
    })

    df_DispK.to_csv(DATA_DIR / "disponibilidad_cirujanos_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 12. DISPONIBILIDAD DE ANESTESISTAS
    # DispM[m,t] = 1 si anestesista m está disponible en tiempo t
    # CSV esperado: m;t;valor
    # ============================================================

    DispM = {}

    for m in range(1, M + 1):
        for t in range(1, T + 1):
            DispM[(m, t)] = 1 if np.random.rand() < 0.85 else 0

    df_DispM = pd.DataFrame({
        "m": [m for m in range(1, M + 1) for t in range(1, T + 1)],
        "t": [t for m in range(1, M + 1) for t in range(1, T + 1)],
        "valor": [DispM[(m, t)] for m in range(1, M + 1) for t in range(1, T + 1)],
    })

    df_DispM.to_csv(DATA_DIR / "disponibilidad_anestesistas_sint.csv", index=False, sep=SEP)


    # ============================================================
    # 13. RESUMEN DE ARCHIVOS CREADOS
    # ============================================================

    archivos = sorted(DATA_DIR.glob("*_sint.csv"))

    print("Datos sintéticos creados correctamente.")
    print(f"Carpeta de salida: {DATA_DIR.resolve()}")
    print(f"Cantidad de pacientes: {I}")
    print(f"Cantidad de bloques horarios: {T}")
    print(f"Cantidad de pabellones: {P}")
    print(f"Cantidad de camas: {C}")
    print(f"Cantidad de cirujanos: {K}")
    print(f"Cantidad de anestesistas: {M}")
    print(f"Cantidad de especialidades: {S}")
    print(f"Cantidad de tipos de cirugía: {CI}")
    print("Validación una cirugía por paciente: OK")
    print("\nArchivos generados:")

    for archivo in archivos:
        print(f"- {archivo}")

    return