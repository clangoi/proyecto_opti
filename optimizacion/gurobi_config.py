import gurobipy as gp
import logging
from datetime import datetime
from optimizacion.logger_setup import LOG_FILE


logging.basicConfig(level=logging.INFO)

def crear_modelo():
    model = gp.Model("Programacion_Pabellones")
    
    model.setParam("OutputFlag", 1)
    model.setParam("LogFile", LOG_FILE)
    model.setParam("MIPFocus", 1)          # Prioriza encontrar solución factible rápido
    model.setParam("Heuristics", 0.15)     # Heurísticas internas moderadas
    model.setParam("Cuts", 2)              # Cortes fuertes activados
    model.setParam("Presolve", 2)          # Presolve agresivo
    model.setParam("Method", -1)           # Auto-seleccionar (mejor para MIP grandes)
    model.setParam("Symmetry", 2)          # Detección agresiva de simetría
    model.setParam("Threads", 0)           # Usar todos los núcleos disponibles
    model.setParam("TimeLimit", 600)       # 10 min (ajusta según hardware)
    model.setParam("MIPGap", 0.01)         # 1% de optimalidad relativa
    model.setParam("PreQLinearize", 1)
    
    return model