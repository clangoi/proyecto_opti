
import time
import os
import gurobipy as gp
from gurobipy import GRB

# CONFIGURACION DE DATOS
DATA_REAL = False  # False: datos sinteticos | True: datos reales
MODELS_DIR = "models" if DATA_REAL else "sintetic_models"
SOLS_DIR = "sols" if DATA_REAL else "sintetic_sols"
FILE_PREFIX = "" if DATA_REAL else "sintetic_"

from create_data import crear_data
crear_data(data=DATA_REAL)

from variables import crear_variables
from funcion_objetivo import agregar_funcion_objetivo
from restricciones import agregar_restricciones
from parametros import crear_parametros
from conjuntos import crear_conjuntos


pacientes, tiempos, pabellones, camas, cirujanos, anestesistas, cirugias, especialidades, tipos_cirugia = crear_conjuntos(data=DATA_REAL) 
alpha, d, r, a, b, L, w, E, Q, R, A, G, DispP, DispK, DispM = crear_parametros(data=DATA_REAL) 

# Crear carpetas de salida automaticamente
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SOLS_DIR, exist_ok=True)


def log(mensaje):
    print(f"[{time.strftime('%H:%M:%S')}] {mensaje}", flush=True)


inicio_total = time.time()

log("Iniciando modelo de programacion quirurgica")
log(f"Modo de datos: {'Real' if DATA_REAL else 'Sintetico'}")

log("Resumen de conjuntos:")
log(f"Pacientes: {len(list(pacientes))}")
log(f"Tiempos: {len(list(tiempos))}")
log(f"Pabellones: {len(list(pabellones))}")
log(f"Camas: {len(list(camas))}")
log(f"Cirujanos: {len(list(cirujanos))}")
log(f"Anestesistas: {len(list(anestesistas))}")
log(f"Tipos de cirugia: {len(list(cirugias))}")
log(f"Especialidades: {len(list(especialidades))}")


# ============================================================
# 1. CREAR MODELO
# ============================================================

log("Creando modelo Gurobi...")
t0 = time.time()

model = gp.Model("Programacion_Pabellones")

log(f"Modelo creado en {time.time() - t0:.2f} segundos")


# ============================================================
# 2. CREAR VARIABLES
# ============================================================

log("Creando variables...")
t0 = time.time()

X, ZI, Z, LQ, WI, W, Y, H, O = crear_variables(
    model=model,
    pacientes=pacientes,
    tiempos=tiempos,
    pabellones=pabellones,
    camas=camas,
    cirujanos=cirujanos,
    anestesistas=anestesistas
)

model.update()

log(f"Variables creadas en {time.time() - t0:.2f} segundos")
log(f"Numero de variables: {model.NumVars}")


# ============================================================
# 3. AGREGAR RESTRICCIONES
# ============================================================

log("Agregando restricciones...")
t0 = time.time()

agregar_restricciones(
    model=model,
    X=X,
    ZI=ZI,
    Z=Z,
    LQ=LQ,
    WI=WI,
    W=W,
    Y=Y,
    H=H,
    O=O,
    pacientes=pacientes,
    tiempos=tiempos,
    pabellones=pabellones,
    camas=camas,
    cirujanos=cirujanos,
    anestesistas=anestesistas,
    cirugias=cirugias,
    especialidades=especialidades,
    G=G,
    E=E,
    A=A,
    Q=Q,
    R=R,
    DispP=DispP,
    DispK=DispK,
    DispM=DispM,
    d=d,
    r=r,
    L=L,
    a=a,
    b=b
)

model.update()

log(f"Restricciones agregadas en {time.time() - t0:.2f} segundos")
log(f"Numero de restricciones: {model.NumConstrs}")


# ============================================================
# 4. AGREGAR FUNCION OBJETIVO
# ============================================================

log("Agregando funcion objetivo...")
t0 = time.time()

agregar_funcion_objetivo(
    model=model,
    X=X,
    O=O,
    pacientes=pacientes,
    pabellones=pabellones,
    tiempos=tiempos,
    w=w,
    alpha=alpha
)

model.update()

log(f"Funcion objetivo agregada en {time.time() - t0:.2f} segundos")


# ============================================================
# 5. CONFIGURACION GUROBI
# ============================================================

log("Configurando parametros de Gurobi...")

model.Params.OutputFlag = 1
model.Params.TimeLimit = 300
model.Params.MIPGap = 0.01

log("Parametros configurados:")
log("OutputFlag = 1")
log("TimeLimit = 300")
log("MIPGap = 0.01")


# ============================================================
# 6. EXPORTAR MODELO ANTES DE OPTIMIZAR
# ============================================================

log("Exportando modelo LP antes de optimizar...")
t0 = time.time()

nombre_modelo = f"{MODELS_DIR}/{FILE_PREFIX}modelo_{time.time():.2f}.lp"
model.write(nombre_modelo)

log(f"Modelo LP exportado en {nombre_modelo} ({time.time() - t0:.2f} s)")


# ============================================================
# 7. OPTIMIZAR
# ============================================================

log("Iniciando optimizacion...")
t0 = time.time()

model.optimize()

log(f"Optimizacion terminada en {time.time() - t0:.2f} segundos")
log(f"Estado del modelo: {model.status}")
log(f"Soluciones encontradas: {model.SolCount}")


# ============================================================
# 8. MOSTRAR RESULTADOS
# ============================================================

if model.status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and model.SolCount > 0:

    print("\n============================================================")
    print("RESULTADOS")
    print("============================================================")

    print(f"\nValor funcion objetivo: {model.ObjVal:.4f}")

    print("\nPacientes programados:")

    cantidad_programados = 0

    for i in pacientes:
        if X[i].X > 0.5:
            cantidad_programados += 1

            for t in tiempos:
                for p in pabellones:
                    if ZI[i, t, p].X > 0.5:
                        print(f"Paciente {i} inicia cirugia en tiempo {t}, pabellon {p}")

                        for k in cirujanos:
                            if Y[i, t, p, k].X > 0.5:
                                print(f"  Cirujano asignado: {k}")

                        for m in anestesistas:
                            if H[i, t, p, m].X > 0.5:
                                print(f"  Anestesista asignado: {m}")

    print(f"\nTotal pacientes programados: {cantidad_programados}")

    print("\nUso de camas de recuperacion:")

    for i in pacientes:
        for t in tiempos:
            for c in camas:
                if WI[i, t, c].X > 0.5:
                    print(f"Paciente {i} inicia recuperacion en tiempo {t}, cama {c}")

else:
    print("\nNo se encontro solucion factible u optima.")
    print(f"Estado del modelo: {model.status}")


# ============================================================
# 9. GUARDAR SOLUCION
# ============================================================

if model.SolCount > 0:
    log("Exportando solucion...")
    nombre_solucion = f"{SOLS_DIR}/{FILE_PREFIX}solucion_{time.time():.2f}.sol"
    model.write(nombre_solucion)
    log(f"Solucion exportada en {nombre_solucion}")


log(f"Tiempo total de ejecucion: {time.time() - inicio_total:.2f} segundos")