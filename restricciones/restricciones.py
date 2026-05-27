# restricciones.py

from .validaciones import validar_datos
from .restricciones_basicas import agregar_restricciones_basicas
from .restricciones_pabellones import agregar_restricciones_pabellones
from .restricciones_personal import agregar_restricciones_personal
from .restricciones_recuperacion import agregar_restricciones_recuperacion


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
    b
):
    validar_datos(
        pacientes=pacientes,
        pabellones=pabellones,
        cirugias=cirugias,
        G=G,
        d=d,
        r=r,
        L=L
    )

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

    return model
