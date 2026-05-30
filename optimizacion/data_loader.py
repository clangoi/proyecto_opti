from create_data import crear_data
from parametros import crear_parametros
from conjuntos import crear_conjuntos


def cargar_datos(data_real=True):
    crear_data(data=data_real)

    pacientes, tiempos, pabellones, camas, cirujanos, anestesistas, cirugias, especialidades, tipos_cirugia = crear_conjuntos(
        data=data_real
    )

    alpha, d, r, a, b, L, w, E, Q, R, A, G, DispP, DispK, DispM = crear_parametros(
        data=data_real
    )

    conjuntos = {
        "pacientes": list(pacientes),
        "tiempos": list(tiempos),
        "pabellones": list(pabellones),
        "camas": list(camas),
        "cirujanos": list(cirujanos),
        "anestesistas": list(anestesistas),
        "cirugias": list(cirugias),
        "especialidades": list(especialidades),
        "tipos_cirugia": list(tipos_cirugia),
    }

    parametros = {
        "alpha": alpha,
        "d": d,
        "r": r,
        "a": a,
        "b": b,
        "L": L,
        "w": w,
        "E": E,
        "Q": Q,
        "R": R,
        "A": A,
        "G": G,
        "DispP": DispP,
        "DispK": DispK,
        "DispM": DispM,
    }

    return conjuntos, parametros