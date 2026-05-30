import gurobipy as gp

def crear_modelo():
    model = gp.Model("Programacion_Pabellones")
    
    model.setParam("OutputFlag", 1)
    
    model.setParam("MIPFocus", 1)          # Prioriza encontrar factibles rápido
    model.setParam("Heuristics", 0.5)      # Más agresivo al inicio (scheduling responde bien)
    model.setParam("Diving", 1)            # Actúa "dives" profundos para cerrar brechas
    model.setParam("RINS", 2)              # Heurística RINS agresiva (excelente para scheduling)
    
    model.setParam("Cuts", 2)              # Cortes automáticos agresivos
    model.setParam("CutsPasses", 5)        # 5 pases en nodo raíz (fortalece LP inicial)
    model.setParam("GomoryPasses", 2)      # Cortes de entericidad fuertes
    model.setParam("FlowCoverCuts", 2)     # CRÍTICO: restrión de pabellón/capacidad
    model.setParam("CliqueCuts", 2)        # Elimina combinaciones incompatibles rápido
    model.setParam("MIRCuts", 2)           # Mixed-Integer Rounding: ideal para packing de horas
    
    model.setParam("Presolve", 2)
    model.setParam("Method", -1)           # Auto-selección (mejor para MIPs grandes)
    model.setParam("Symmetry", 2)          # Detección agresiva de simetría (horarios idénticos)
    model.setParam("BranchDir", 1)         # Explora primero rama "down" (mejor para fijar 0/1)
    model.setParam("StartNodeLimit", 50)   # Explora 50 nodos antes de lanzar heurísticas pesadas
    
    model.setParam("Threads", 0)           # Todos los núcleos
    model.setParam("Parallel", 1)          # Paralelismo automático
    model.setParam("TimeLimit", 600)       # 10 min
    model.setParam("MIPGap", 0.02)         # 2% es práctico y evita estancamiento en el 0.1%
    
    return model