# main.py

import time
import gurobipy as gp
from gurobipy import GRB

from create_data import crear_data
crear_data(data=False)

from variables import crear_variables
from funcion_objetivo import agregar_funcion_objetivo
from restricciones import agregar_restricciones
from parametros import crear_parametros
from conjuntos import crear_conjuntos


pacientes, tiempos, pabellones, camas, cirujanos, anestesistas, cirugias, especialidades, tipos_cirugia = crear_conjuntos(data=False) 
alpha, d, r, a, b, L, w, E, Q, R, A, G, DispP, DispK, DispM = crear_parametros(data=False) 



def log(mensaje):
    print(f"[{time.strftime('%H:%M:%S')}] {mensaje}", flush=True)


inicio_total = time.time()

log("Iniciando modelo de programación quirúrgica")

log("Resumen de conjuntos:")
log(f"Pacientes: {len(list(pacientes))}")
log(f"Tiempos: {len(list(tiempos))}")
log(f"Pabellones: {len(list(pabellones))}")
log(f"Camas: {len(list(camas))}")
log(f"Cirujanos: {len(list(cirujanos))}")
log(f"Anestesistas: {len(list(anestesistas))}")
log(f"Tipos de cirugía: {len(list(cirugias))}")
log(f"Especialidades: {len(list(especialidades))}")


# ============================================================
# 1. CREAR MODELO
# ============================================================

log("Creando modelo Gurobi...")
t0 = time.time()

model = gp.Model("Programacion_Quirurgica")

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
log(f"Número de variables: {model.NumVars}")


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
log(f"Número de restricciones: {model.NumConstrs}")


# ============================================================
# 4. AGREGAR FUNCIÓN OBJETIVO
# ============================================================

log("Agregando función objetivo...")
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

log(f"Función objetivo agregada en {time.time() - t0:.2f} segundos")


# ============================================================
# 5. CONFIGURACIÓN GUROBI
# ============================================================

log("Configurando parámetros de Gurobi...")

model.Params.OutputFlag = 1
model.Params.TimeLimit = 300
model.Params.MIPGap = 0.01

log("Parámetros configurados:")
log("OutputFlag = 1")
log("TimeLimit = 300")
log("MIPGap = 0.01")


# ============================================================
# 6. EXPORTAR MODELO ANTES DE OPTIMIZAR
# ============================================================

log("Exportando modelo LP antes de optimizar...")
t0 = time.time()

model.write("modelo_programacion_{:.2f}.lp".format(time.time()))

log(f"Modelo LP exportado en {time.time() - t0:.2f} segundos")


# ============================================================
# 7. OPTIMIZAR
# ============================================================

log("Iniciando optimización...")
t0 = time.time()

model.optimize()

log(f"Optimización terminada en {time.time() - t0:.2f} segundos")
log(f"Estado del modelo: {model.status}")
log(f"Soluciones encontradas: {model.SolCount}")


# ============================================================
# 8. MOSTRAR RESULTADOS
# ============================================================

if model.status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and model.SolCount > 0:

    print("\n============================================================")
    print("RESULTADOS")
    print("============================================================")

    print(f"\nValor función objetivo: {model.ObjVal:.4f}")

    print("\nPacientes programados:")

    cantidad_programados = 0

    for i in pacientes:
        if X[i].X > 0.5:
            cantidad_programados += 1

            for t in tiempos:
                for p in pabellones:
                    if ZI[i, t, p].X > 0.5:
                        print(f"Paciente {i} inicia cirugía en tiempo {t}, pabellón {p}")

                        for k in cirujanos:
                            if Y[i, t, p, k].X > 0.5:
                                print(f"  Cirujano asignado: {k}")

                        for m in anestesistas:
                            if H[i, t, p, m].X > 0.5:
                                print(f"  Anestesista asignado: {m}")

    print(f"\nTotal pacientes programados: {cantidad_programados}")

    print("\nUso de camas de recuperación:")

    for i in pacientes:
        for t in tiempos:
            for c in camas:
                if WI[i, t, c].X > 0.5:
                    print(f"Paciente {i} inicia recuperación en tiempo {t}, cama {c}")

else:
    print("\nNo se encontró solución factible u óptima.")
    print(f"Estado del modelo: {model.status}")


# ============================================================
# 9. GUARDAR SOLUCIÓN
# ============================================================

if model.SolCount > 0:
    log("Exportando solución...")
    model.write("solucion_programacion_quirurgica.sol")
    log("Solución exportada en solucion_programacion_quirurgica.sol")


log(f"Tiempo total de ejecución: {time.time() - inicio_total:.2f} segundos")