from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

# ============================================================
# 0. PARÁMETROS GLOBALES, RUTAS Y CONFIGURACIÓN
# ============================================================
SEP = ";"
SEED = 42
BASE_DIR = Path("data")
DATA_DIR = Path("data")
ENCODING = "utf-8"

INPUT_FILES = {
    "parametros_globales": BASE_DIR / "parametros_globales.csv",
    "parametros_cirugia": BASE_DIR / "parametros_cirugia.csv",
    "nombres_cirugia": BASE_DIR / "CI.csv",
    "especialidades": BASE_DIR / "S.csv",
    "cirujanos": BASE_DIR / "K.csv",
}

INPUT_FALLBACKS = {
    "parametros_cirugia": [
        BASE_DIR / "parametros_cirugia.csv",
        BASE_DIR / "parametros cirugia.csv",
        BASE_DIR / "parametros cirugia(3).csv",
        BASE_DIR / "parametros cirugia(2).csv",
        BASE_DIR / "parametros cirugia(1).csv",
    ],
    "nombres_cirugia": [
        BASE_DIR / "CI.csv",
        BASE_DIR / "ci.csv",
    ],
    "cirujanos": [
        BASE_DIR / "K.csv",
        BASE_DIR / "K(1).csv",
    ],
}

OUTPUT_FILES = {
    "limpieza_pabellones": DATA_DIR / "limpieza_pabellones.csv",
    "prioridad_pacientes": DATA_DIR / "prioridad_pacientes.csv",
    "especialidad_cirugia": DATA_DIR / "especialidad_cirugia.csv",
    "cirujano_cirugia": DATA_DIR / "cirujano_cirugia.csv",
    "anestesista_cirugia": DATA_DIR / "anestesista_cirugia.csv",
    "pabellon_especialidad": DATA_DIR / "pabellon_especialidad.csv",
    "paciente_cirugia": DATA_DIR / "paciente_cirugia.csv",
    "disponibilidad_pabellones": DATA_DIR / "disponibilidad_pabellones.csv",
    "disponibilidad_cirujanos": DATA_DIR / "disponibilidad_cirujanos.csv",
    "disponibilidad_anestesistas": DATA_DIR / "disponibilidad_anestesistas.csv",
}

# ============================================================
# 0.1 RELACIONES BASE
# ============================================================

RELACION_CI_S = {
    1: [1],
    2: [1, 2, 3, 15],
    3: [2],
    4: [3],
    5: [4],
    6: [5, 17],
    7: [6],
    8: [7],
    9: [8],
    10: [9],
    11: [10],
    12: [1, 2, 3, 6, 7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19],
    13: [1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    14: [1, 2, 3, 6, 8, 9, 11, 12, 15, 16, 17],
    15: [11],
    16: [12],
    17: [13],
    18: [14],
    19: [15],
    20: [15],
    21: [16],
    22: [17],
    23: [18],
    24: [19],
}

RELACION_CI_K = {
    1: [1, 2, 6],
    2: [1, 2, 3, 4, 6, 20],
    3: [3, 4],
    4: [5, 6],
    5: [7, 8],
    6: [9, 10],
    7: [11],
    8: [12],
    9: [13],
    10: [14],
    11: [15],
    12: [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 14, 15, 18, 19, 20, 21, 22, 23],
    13: [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23],
    14: [1, 2, 3, 4, 5, 6, 9, 10, 11, 13, 14, 16, 17, 20, 21, 22],
    15: [16],
    16: [17],
    17: [18],
    18: [19],
    19: [20, 21],
    20: [20, 21],
    21: [22],
    22: [9, 10],
    23: [23],
    24: [23],
}

PESOS_CI = {
    1: 0.035,
    2: 0.055,
    3: 0.051,
    4: 0.078,
    5: 0.025,
    6: 0.008,
    7: 0.012,
    8: 0.012,
    9: 0.005,
    10: 0.008,
    11: 0.010,
    12: 0.025,
    13: 0.025,
    14: 0.010,
    15: 0.012,
    16: 0.010,
    17: 0.069,
    18: 0.072,
    19: 0.073,
    20: 0.015,
    21: 0.224,
    22: 0.012,
    23: 0.129,
    24: 0.025,
}

# ============================================================
# 1. FUNCIONES AUXILIARES
# ============================================================

def resolve_input(name: str) -> Path:
    candidates = [INPUT_FILES[name], *INPUT_FALLBACKS.get(name, [])]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        f"No encontré el archivo de entrada '{name}'. Rutas revisadas: "
        + ", ".join(str(p) for p in candidates)
    )


def read_csv(name: str) -> pd.DataFrame:
    path = resolve_input(name)
    df = pd.read_csv(path, sep=SEP, encoding=ENCODING)
    df.columns = df.columns.str.strip()
    return df


def write_csv(df: pd.DataFrame, output_key: str) -> None:
    path = OUTPUT_FILES[output_key]
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep=SEP, index=False, encoding=ENCODING)


def normalize_columns(df: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    normalized = {col.strip().lower(): col for col in df.columns}
    rename_real = {}

    for original, new in rename_map.items():
        key = original.strip().lower()
        if key in normalized:
            rename_real[normalized[key]] = new

    return df.rename(columns=rename_real)


def load_global_params() -> dict[str, int]:
    df = read_csv("parametros_globales")
    df = normalize_columns(df, {"parametro": "parametro", "valor": "valor"})

    df["parametro"] = df["parametro"].astype(str).str.strip().str.upper()
    params = df.set_index("parametro")["valor"].astype(int).to_dict()

    required = ["I", "T", "P", "C", "K", "M", "S", "CI"]
    missing = [p for p in required if p not in params]

    if missing:
        raise ValueError(f"Faltan parámetros globales: {missing}")

    return params


def load_cirugias() -> pd.DataFrame:
    """
    Lee:
    - parametros_cirugia.csv con columnas: ci;d;r;a;b
    - CI.csv con columnas: CI;nombre cirugia

    Devuelve un DataFrame con:
    ci, d, r, a, b, nombre_cirugia
    """

    parametros = read_csv("parametros_cirugia")
    parametros = normalize_columns(
        parametros,
        {
            "ci": "ci",
            "CI": "ci",
            "d": "d",
            "r": "r",
            "a": "a",
            "b": "b",
        },
    )

    required_parametros = ["ci", "d", "r", "a", "b"]
    missing_parametros = [c for c in required_parametros if c not in parametros.columns]

    if missing_parametros:
        raise ValueError(
            f"parametros_cirugia.csv debe tener columnas {required_parametros}. "
            f"Faltan: {missing_parametros}"
        )

    parametros["ci"] = parametros["ci"].astype(int)
    parametros["d"] = parametros["d"].astype(int)
    parametros["r"] = parametros["r"].astype(int)
    parametros["a"] = parametros["a"].astype(int)
    parametros["b"] = parametros["b"].astype(int)

    parametros = (
        parametros[["ci", "d", "r", "a", "b"]]
        .drop_duplicates(subset=["ci"])
        .sort_values("ci")
        .reset_index(drop=True)
    )

    nombres = read_csv("nombres_cirugia")
    nombres = normalize_columns(
        nombres,
        {
            "ci": "ci",
            "CI": "ci",
            "nombre cirugia": "nombre_cirugia",
            "nombre_cirugia": "nombre_cirugia",
        },
    )

    required_nombres = ["ci", "nombre_cirugia"]
    missing_nombres = [c for c in required_nombres if c not in nombres.columns]

    if missing_nombres:
        raise ValueError(
            f"CI.csv debe tener columnas {required_nombres}. "
            f"Faltan: {missing_nombres}"
        )

    nombres["ci"] = nombres["ci"].astype(int)
    nombres["nombre_cirugia"] = nombres["nombre_cirugia"].astype(str).str.strip()

    nombres = (
        nombres[["ci", "nombre_cirugia"]]
        .drop_duplicates(subset=["ci"])
        .sort_values("ci")
        .reset_index(drop=True)
    )

    df = parametros.merge(nombres, on="ci", how="left")

    if df["nombre_cirugia"].isna().any():
        faltantes = df.loc[df["nombre_cirugia"].isna(), "ci"].tolist()
        raise ValueError(f"Faltan nombres en CI.csv para estos ci: {faltantes}")

    return df.sort_values("ci").reset_index(drop=True)


def load_especialidades() -> pd.DataFrame:
    df = read_csv("especialidades")
    df = normalize_columns(df, {"S": "s", "s": "s", "Especialidad": "especialidad"})

    if "s" not in df.columns:
        raise ValueError("S.csv debe tener columna 'S' o 's'.")

    df["s"] = df["s"].astype(int)

    return df.drop_duplicates(subset=["s"]).sort_values("s").reset_index(drop=True)


def load_cirujanos() -> pd.DataFrame:
    df = read_csv("cirujanos")
    df = normalize_columns(df, {"K": "k", "k": "k", "Tipo de cirujano": "tipo_cirujano"})

    if "k" not in df.columns:
        raise ValueError("K.csv debe tener columna 'K' o 'k'.")

    df["k"] = df["k"].astype(int)

    return df.drop_duplicates(subset=["k"]).sort_values("k").reset_index(drop=True)


def cross_join(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    return left.merge(right, how="cross")


def relation_frame(
    mapping: dict[int, Iterable[int]],
    left_col: str,
    right_col: str,
) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            (left_id, right_id)
            for left_id, right_ids in mapping.items()
            for right_id in right_ids
        ],
        columns=[left_col, right_col],
    )

    df["valor"] = 1
    return df


def generate_availability_blocks(
    resource_ids: Iterable[int],
    resource_col: str,
    T: int,
    rng: np.random.Generator,
    min_work: int = 4,
    max_work: int = 8,
    min_rest: int = 1,
    max_rest: int = 2,
    prob_start_working: float = 0.80,
) -> pd.DataFrame:
    rows = []

    for resource_id in resource_ids:
        t = 1
        state = 1 if rng.random() < prob_start_working else 0

        while t <= T:
            if state == 1:
                duration = int(rng.integers(min_work, max_work + 1))
            else:
                duration = int(rng.integers(min_rest, max_rest + 1))

            end_t = min(T, t + duration - 1)

            rows.extend(
                {
                    resource_col: resource_id,
                    "t": tt,
                    "valor": state,
                }
                for tt in range(t, end_t + 1)
            )

            t = end_t + 1
            state = 1 - state

    return pd.DataFrame(rows).sort_values([resource_col, "t"]).reset_index(drop=True)


# ============================================================
# 2. GENERADORES DE ARCHIVOS
# ============================================================

def generar_limpieza_pabellones(P: int, rng: np.random.Generator) -> None:
    df = pd.DataFrame(
        {
            "p": np.arange(1, P + 1),
            "L": rng.integers(1, 4, size=P),
        }
    )

    write_csv(df[["p", "L"]], "limpieza_pabellones")


def generar_prioridad_pacientes(I: int, rng: np.random.Generator) -> None:
    w = np.clip(
        np.round(rng.normal(loc=5.5, scale=2.0, size=I)),
        1,
        10,
    ).astype(int)

    df = pd.DataFrame(
        {
            "i": np.arange(1, I + 1),
            "w": w,
        }
    )

    write_csv(df[["i", "w"]], "prioridad_pacientes")


def generar_especialidad_cirugia(
    cirugias: pd.DataFrame,
    especialidades: pd.DataFrame,
) -> None:
    relaciones = relation_frame(RELACION_CI_S, "ci", "s")

    df = cross_join(cirugias[["ci"]], especialidades[["s"]])
    df = df.merge(relaciones, on=["ci", "s"], how="left")
    df["valor"] = df["valor"].fillna(0).astype(int)
    df = df.sort_values(["ci", "s"])

    write_csv(df[["ci", "s", "valor"]], "especialidad_cirugia")


def generar_cirujano_cirugia(
    cirugias: pd.DataFrame,
    cirujanos: pd.DataFrame,
) -> None:
    relaciones = relation_frame(RELACION_CI_K, "ci", "k")

    df = cross_join(cirugias[["ci"]], cirujanos[["k"]])
    df = df.merge(relaciones, on=["ci", "k"], how="left")
    df["valor"] = df["valor"].fillna(0).astype(int)
    df = df.sort_values(["ci", "k"])

    write_csv(df[["ci", "k", "valor"]], "cirujano_cirugia")


def generar_anestesista_cirugia(
    cirugias: pd.DataFrame,
    M: int,
) -> None:
    infantil = cirugias.loc[
        cirugias["nombre_cirugia"].str.lower().str.contains("infantil", na=False),
        "ci",
    ]

    if infantil.empty:
        raise ValueError("No encontré una cirugía con nombre que contenga 'infantil' en CI.csv.")

    ci_infantil = int(infantil.iloc[0])
    m_infantil = M

    anestesistas = pd.DataFrame({"m": np.arange(1, M + 1)})

    df = cross_join(cirugias[["ci"]], anestesistas)

    df["valor"] = (
        (df["ci"] != ci_infantil)
        | (df["m"] == m_infantil)
    ).astype(int)

    df = df.sort_values(["ci", "m"])

    write_csv(df[["ci", "m", "valor"]], "anestesista_cirugia")


def generar_pabellon_especialidad(
    P: int,
    S: int,
    rng: np.random.Generator,
) -> None:
    df = pd.DataFrame(
        {
            "p": np.repeat(np.arange(1, P + 1), S),
            "s": np.tile(np.arange(1, S + 1), P),
        }
    )

    df["valor"] = 0

    compatible_pairs = []

    for s in range(1, S + 1):
        selected_p = rng.choice(
            np.arange(1, P + 1),
            size=min(2, P),
            replace=False,
        )

        compatible_pairs.extend((int(p), s) for p in selected_p)

    base = pd.DataFrame(compatible_pairs, columns=["p", "s"])
    base["valor_base"] = 1

    df = df.merge(base, on=["p", "s"], how="left")

    extra = rng.random(len(df)) < 0.25

    df["valor"] = (
        (df["valor_base"].fillna(0).astype(int) == 1)
        | extra
    ).astype(int)

    df = df.drop(columns="valor_base")
    df = df.sort_values(["p", "s"])

    write_csv(df[["p", "s", "valor"]], "pabellon_especialidad")


def generar_paciente_cirugia(
    cirugias: pd.DataFrame,
    I: int,
    rng: np.random.Generator,
) -> None:
    ci_archivo = set(cirugias["ci"])
    faltan_pesos = ci_archivo - set(PESOS_CI.keys())

    if faltan_pesos:
        raise ValueError(f"Faltan pesos para estos CI: {sorted(faltan_pesos)}")

    cirugias_prob = cirugias[["ci"]].copy()
    cirugias_prob["peso"] = cirugias_prob["ci"].map(PESOS_CI)
    cirugias_prob["probabilidad"] = cirugias_prob["peso"] / cirugias_prob["peso"].sum()

    pacientes = pd.DataFrame({"i": np.arange(1, I + 1)})

    asignaciones = pd.DataFrame(
        {
            "i": pacientes["i"],
            "ci_asignado": rng.choice(
                cirugias_prob["ci"].to_numpy(),
                size=I,
                replace=True,
                p=cirugias_prob["probabilidad"].to_numpy(),
            ),
        }
    )

    df = cross_join(pacientes, cirugias_prob[["ci"]])
    df = df.merge(asignaciones, on="i", how="left")
    df["valor"] = (df["ci"] == df["ci_asignado"]).astype(int)
    df = df.sort_values(["i", "ci"])

    validacion = df.groupby("i")["valor"].sum()

    if not (validacion == 1).all():
        raise ValueError("Hay pacientes con cero o más de una cirugía asignada.")

    write_csv(df[["i", "ci", "valor"]], "paciente_cirugia")


def generar_disponibilidad_pabellones(P: int, T: int) -> None:
    df = pd.DataFrame(
        {
            "p": np.repeat(np.arange(1, P + 1), T),
            "t": np.tile(np.arange(1, T + 1), P),
            "valor": 1,
        }
    )

    write_csv(df[["p", "t", "valor"]], "disponibilidad_pabellones")


def generar_disponibilidad_cirujanos(
    K: int,
    T: int,
    rng: np.random.Generator,
) -> None:
    df = generate_availability_blocks(
        resource_ids=range(1, K + 1),
        resource_col="k",
        T=T,
        rng=rng,
    )

    write_csv(df[["k", "t", "valor"]], "disponibilidad_cirujanos")


def generar_disponibilidad_anestesistas(
    M: int,
    T: int,
    rng: np.random.Generator,
) -> None:
    df = generate_availability_blocks(
        resource_ids=range(1, M + 1),
        resource_col="m",
        T=T,
        rng=rng,
    )

    write_csv(df[["m", "t", "valor"]], "disponibilidad_anestesistas")


# ============================================================
# 3. EJECUCIÓN
# ============================================================

def main() -> None:
    rng = np.random.default_rng(SEED)

    params = load_global_params()

    I = params["I"]
    T = params["T"]
    P = params["P"]
    K = params["K"]
    M = params["M"]
    S = params["S"]

    cirugias = load_cirugias()
    especialidades = load_especialidades()
    cirujanos = load_cirujanos()

    generar_limpieza_pabellones(P, rng)
    generar_prioridad_pacientes(I, rng)
    generar_especialidad_cirugia(cirugias, especialidades)
    generar_cirujano_cirugia(cirugias, cirujanos)
    generar_anestesista_cirugia(cirugias, M)
    generar_pabellon_especialidad(P, S, rng)
    generar_paciente_cirugia(cirugias, I, rng)
    generar_disponibilidad_pabellones(P, T)
    generar_disponibilidad_cirujanos(K, T, rng)
    generar_disponibilidad_anestesistas(M, T, rng)

    print("Archivos generados en:", DATA_DIR)

    for key, path in OUTPUT_FILES.items():
        print(f"- {key}: {path.name}")


if __name__ == "__main__":
    main()