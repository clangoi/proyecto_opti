# ============================================================
# 1. PARÁMETROS GLOBALES (importar de csv luego)
# ============================================================
import pandas as pd

def crear_conjuntos(data):

    # data True para datos reales, False para datos sintéticos
    if data:
        df_globales = pd.read_csv("data/parametros_globales.csv")
    else:
        df_globales = pd.read_csv("data_sintetica/data/parametros_globales_sint.csv", sep=";")

    globales = {
    row["parametro"]: int(row["valor"])
    for _, row in df_globales.iterrows()
    }

    I = globales["I"]     # Pacientes
    T = globales["T"]     # Bloques horarios
    P = globales["P"]     # Pabellones
    C = globales["C"]     # Camas
    K = globales["K"]     # Cirujanos
    M = globales["M"]     # Anestesistas
    S = globales["S"]     # Especialidades
    CI = globales["CI"]   # Tipos de cirugía


    # ============================================================
    # 2. GENERACIÓN DE CONJUNTOS
    # ============================================================

    pacientes = range(1, I + 1)        # i ∈ {1,...,I}
    tiempos = range(1, T + 1)          # t ∈ {1,...,T}
    pabellones = range(1, P + 1)       # p ∈ {1,...,P}
    camas = range(1, C + 1)            # c ∈ {1,...,C}
    cirujanos = range(1, K + 1)        # k ∈ {1,...,K}
    anestesistas = range(1, M + 1)     # m ∈ {1,...,M}
    especialidades = range(1, S + 1)   # s ∈ {1,...,S}
    cirugias = range(1, CI + 1)        # ci ∈ {1,...,CI}


    # ============================================================
    # 3. TIPOS DE CIRUGÍA POR PACIENTE
    # ============================================================

    Ci_por_paciente = {
    i: [1, 2] for i in pacientes
    }

    # Si todos los pacientes tienen un único tipo de cirugía:
    # Ci_por_paciente = {i: [1] for i in pacientes}

    tipos_cirugia = {
    i: Ci_por_paciente[i] for i in pacientes
    }

    return pacientes, tiempos, pabellones, camas, cirujanos, anestesistas, cirugias, especialidades, tipos_cirugia