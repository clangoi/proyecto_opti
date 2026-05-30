import time
import os
import gurobipy as gp
from gurobipy import GRB

# ============================================================
# CONFIGURACION GENERAL
# ============================================================

DATA_REAL = True  # False: datos sinteticos | True: datos reales

MODELS_DIR = "models" if DATA_REAL else "sintetic_models"
SOLS_DIR = "soluciones" if DATA_REAL else "sintetic_sols"
FILE_PREFIX = "" if DATA_REAL else "sintetic_"

LIMPIEZA_BLOQUES = 1

EXPORTAR_LP = True
USAR_WARM_START = True

# ============================================================
# IMPORTS DEL PROYECTO
# ============================================================

from create_data import crear_data
from variables import crear_variables
from funcion_objetivo import agregar_funcion_objetivo
from restricciones import agregar_restricciones
from parametros import crear_parametros
from conjuntos import crear_conjuntos

try:
    from optimizacion.warm_start import aplicar_warm_start_factible
    WARM_START_DISPONIBLE = True
except ImportError:
    WARM_START_DISPONIBLE = False


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def log(mensaje):
    print(f"[{time.strftime('%H:%M:%S')}] {mensaje}", flush=True)


def positivos_2d(diccionario):
    return {
        key for key, value in diccionario.items()
        if value == 1
    }


def construir_ci_paciente(G):
    """
    G[i,ci] = 1 si paciente i requiere cirugía ci.
    Devuelve ci_paciente[i] = ci.
    """
    ci_paciente = {}

    for (i, ci), valor in G.items():
        if valor == 1:
            if i in ci_paciente:
                raise ValueError(
                    f"El paciente {i} tiene más de una cirugía asignada: "
                    f"{ci_paciente[i]} y {ci}"
                )
            ci_paciente[i] = ci

    return ci_paciente


def validar_ci_paciente(pacientes, ci_paciente):
    pacientes_sin_cirugia = [
        i for i in pacientes
        if i not in ci_paciente
    ]

    if pacientes_sin_cirugia:
        raise ValueError(
            f"Hay pacientes sin cirugía asignada en G: {pacientes_sin_cirugia[:20]}"
        )


def imprimir_resumen_variables(X, ZI, Z, LQ, WI, W, Y, H, O):
    log("Detalle de variables:")
    log(f"X:  {len(X)}")
    log(f"ZI: {len(ZI)}")
    log(f"Z:  {len(Z)}")
    log(f"LQ: {len(LQ)}")
    log(f"WI: {len(WI)}")
    log(f"W:  {len(W)}")
    log(f"Y:  {len(Y)}")
    log(f"H:  {len(H)}")
    log(f"O:  {len(O)}")


# ============================================================
# INICIO
# ============================================================

inicio_total = time.time()

log("Iniciando modelo de programacion quirurgica")
log(f"Modo de datos: {'Real' if DATA_REAL else 'Sintetico'}")


# ============================================================
# 0. CREAR / ACTUALIZAR DATOS
# ============================================================

log("Creando/cargando datos...")
t0 = time.time()

crear_data(data=DATA_REAL)

log(f"Datos listos en {time.time() - t0:.2f} segundos")


# ============================================================
# 1. CARGAR CONJUNTOS Y PARAMETROS
# ============================================================

log("Cargando conjuntos...")
t0 = time.time()

pacientes, tiempos, pabellones, camas, cirujanos, anestesistas, cirugias, especialidades, tipos_cirugia = crear_conjuntos(
    data=DATA_REAL
)

pacientes = list(pacientes)
tiempos = list(tiempos)
pabellones = list(pabellones)
camas = list(camas)
cirujanos = list(cirujanos)
anestesistas = list(anestesistas)
cirugias = list(cirugias)
especialidades = list(especialidades)

log(f"Conjuntos cargados en {time.time() - t0:.2f} segundos")

log("Cargando parametros...")
t0 = time.time()

alpha, d, r, a, b, L, w, E, Q, R, A, G, DispP, DispK, DispM = crear_parametros(
    data=DATA_REAL
)

log(f"Parametros cargados en {time.time() - t0:.2f} segundos")


# ============================================================
# 2. PREPROCESAMIENTO PARA REDUCCION ESTRUCTURAL
# ============================================================

log("Construyendo estructuras auxiliares para pre-filtering...")
t0 = time.time()

ci_paciente = construir_ci_paciente(G)
validar_ci_paciente(pacientes, ci_paciente)

DispP_pos = positivos_2d(DispP)
DispK_pos = positivos_2d(DispK)
DispM_pos = positivos_2d(DispM)

# Q[ci,k] = 1 si cirujano k puede hacer cirugía ci
# A[ci,m] = 1 si anestesista m puede asistir cirugía ci
CK_pos = positivos_2d(Q)
CM_pos = positivos_2d(A)

log(f"Pre-filtering preparado en {time.time() - t0:.2f} segundos")


# ============================================================
# 3. CREAR CARPETAS DE SALIDA
# ============================================================

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SOLS_DIR, exist_ok=True)


# ============================================================
# 4. RESUMEN DE CONJUNTOS
# ============================================================

log("Resumen de conjuntos:")
log(f"Pacientes: {len(pacientes)}")
log(f"Tiempos: {len(tiempos)}")
log(f"Pabellones: {len(pabellones)}")
log(f"Camas: {len(camas)}")
log(f"Cirujanos: {len(cirujanos)}")
log(f"Anestesistas: {len(anestesistas)}")
log(f"Tipos de cirugia: {len(cirugias)}")
log(f"Especialidades: {len(especialidades)}")

log("Resumen de pre-filtering:")
log(f"Pacientes con cirugía asignada: {len(ci_paciente)}")
log(f"Disponibilidad pabellones positiva: {len(DispP_pos)}")
log(f"Disponibilidad cirujanos positiva: {len(DispK_pos)}")
log(f"Disponibilidad anestesistas positiva: {len(DispM_pos)}")
log(f"Compatibilidad cirugía-cirujano positiva: {len(CK_pos)}")
log(f"Compatibilidad cirugía-anestesista positiva: {len(CM_pos)}")


# ============================================================
# 5. CREAR MODELO
# ============================================================

log("Creando modelo Gurobi...")
t0 = time.time()

model = gp.Model("Programacion_Pabellones")

# ============================================================
# PARAMETROS GUROBI
# ============================================================

# Silencia logs internos de Gurobi. No silencia tus print() ni log().
model.setParam("OutputFlag", 0)

# Method = 1 corresponde a dual simplex.
# Method = 0 es primal simplex.
model.setParam("Method", 1)

# Presolve agresivo. Esto reemplaza a model.preset(2).
model.setParam("Presolve", 2)

model.setParam("MIPFocus", 1)
model.setParam("Heuristics", 0.1)
model.setParam("Cuts", 2)
model.setParam("Symmetry", 2)

model.setParam("MIPGap", 0.01)
model.setParam("TimeLimit", 300)

model.setParam("Threads", 0)

log(f"Modelo creado en {time.time() - t0:.2f} segundos")


# ============================================================
# 6. CREAR VARIABLES CON PRE-FILTERING
# ============================================================

log("Creando variables con pre-filtering...")
t0 = time.time()

X, ZI, Z, LQ, WI, W, Y, H, O = crear_variables(
    model=model,
    pacientes=pacientes,
    tiempos=tiempos,
    pabellones=pabellones,
    camas=camas,
    cirujanos=cirujanos,
    anestesistas=anestesistas,
    ci_paciente=ci_paciente,
    duracion_cirugia=d,
    duracion_recuperacion=r,
    limpieza=LIMPIEZA_BLOQUES,
    DispP_pos=DispP_pos,
    DispK_pos=DispK_pos,
    DispM_pos=DispM_pos,
    CK_pos=CK_pos,
    CM_pos=CM_pos
)

model.update()

log(f"Variables creadas en {time.time() - t0:.2f} segundos")
log(f"Numero de variables: {model.NumVars}")
imprimir_resumen_variables(X, ZI, Z, LQ, WI, W, Y, H, O)


# ============================================================
# 7. AGREGAR RESTRICCIONES OPTIMIZADAS
# ============================================================

log("Agregando restricciones optimizadas...")
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
    b=b,
    usar_update_final=True
)

log(f"Restricciones agregadas en {time.time() - t0:.2f} segundos")
log(f"Numero de restricciones: {model.NumConstrs}")


# ============================================================
# 8. AGREGAR FUNCION OBJETIVO
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
# 9. WARM START FACTIBLE
# ============================================================

if USAR_WARM_START:
    if WARM_START_DISPONIBLE:
        log("Aplicando warm start factible...")
        t0 = time.time()

        aplicar_warm_start_factible(
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
            d=d,
            r=r,
            L=L,
            G=G,
            cirugias=cirugias,
            DispP=DispP,
            E=E,
            A=A,
            a=a,
            b=b,
            especialidades=especialidades,
            max_pacientes=None,
            verbose=True
        )

        log(f"Warm start aplicado en {time.time() - t0:.2f} segundos")
    else:
        log("Warm start activado, pero no existe warm_start.py. Se continúa sin warm start.")


# ============================================================
# 10. EXPORTAR MODELO ANTES DE OPTIMIZAR
# ============================================================

if EXPORTAR_LP:
    log("Exportando modelo LP antes de optimizar...")
    t0 = time.time()

    timestamp = f"{time.time():.2f}"
    nombre_modelo = f"{MODELS_DIR}/{FILE_PREFIX}modelo_{timestamp}.lp"

    model.write(nombre_modelo)

    log(f"Modelo LP exportado en {nombre_modelo} ({time.time() - t0:.2f} s)")


# ============================================================
# 11. OPTIMIZAR
# ============================================================

log("Iniciando optimizacion...")
t0 = time.time()

model.optimize()

log(f"Optimizacion terminada en {time.time() - t0:.2f} segundos")
log(f"Estado del modelo: {model.status}")
log(f"Soluciones encontradas: {model.SolCount}")


# ============================================================
# 12. MOSTRAR RESULTADOS
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
                    if (i, t, p) in ZI and ZI[i, t, p].X > 0.5:
                        print(f"Paciente {i} inicia cirugia en tiempo {t}, pabellon {p}")

                        for k in cirujanos:
                            if (i, t, p, k) in Y and Y[i, t, p, k].X > 0.5:
                                print(f"  Cirujano asignado: {k}")

                        for m in anestesistas:
                            if (i, t, p, m) in H and H[i, t, p, m].X > 0.5:
                                print(f"  Anestesista asignado: {m}")

    print(f"\nTotal pacientes programados: {cantidad_programados}")

    print("\nUso de camas de recuperacion:")

    for i in pacientes:
        for t in tiempos:
            for c in camas:
                if (i, t, c) in WI and WI[i, t, c].X > 0.5:
                    print(f"Paciente {i} inicia recuperacion en tiempo {t}, cama {c}")

else:
    print("\nNo se encontro solucion factible u optima.")
    print(f"Estado del modelo: {model.status}")


# ============================================================
# 13. GUARDAR SOLUCION
# ============================================================

if model.SolCount > 0:
    log("Exportando solucion...")

    timestamp = f"{time.time():.2f}"
    nombre_solucion = f"{SOLS_DIR}/{FILE_PREFIX}solucion_{timestamp}.sol"

    model.write(nombre_solucion)

    log(f"Solucion exportada en {nombre_solucion}")


# ============================================================
# 14. FIN
# ============================================================

log(f"Tiempo total de ejecucion: {time.time() - inicio_total:.2f} segundos")