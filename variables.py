from gurobipy import GRB

def crear_variables(
    model, pacientes, tiempos, pabellones, camas, cirujanos, anestesistas,
    ci_paciente, duracion_cirugia, duracion_recuperacion, limpieza,
    DispP_pos, DispK_pos, DispM_pos, CK_pos, CM_pos, ventanas_pacientes=None
):
    tiempos = sorted(tiempos)
    T_MAX = tiempos[-1]
    
    d_cir = {ci: int(d) for ci, d in duracion_cirugia.items()}
    r_rec = {ci: int(r) for ci, r in duracion_recuperacion.items()}

    # Convertir a sets para búsquedas O(1)
    dp = set(DispP_pos)
    dk = set(DispK_pos)
    dm = set(DispM_pos)
    ck = set(CK_pos)
    cm = set(CM_pos)

    X = model.addVars(pacientes, vtype=GRB.BINARY, name="X")

    # 🔑 PASO 1: Identificar combinaciones (i,t,p) VIABLES (con Y y H garantizados)
    ZI_keys = []
    Y_keys = []
    H_keys = []
    
    for i in pacientes:
        ci = ci_paciente[i]
        d = d_cir[ci]
        t_min, t_max = ventanas_pacientes.get(i, (tiempos[0], T_MAX)) if ventanas_pacientes else (tiempos[0], T_MAX)

        for t in tiempos:
            if t < t_min or t > t_max: continue
            if t + d - 1 > T_MAX: continue
            
            bloques = range(t, t + d)
            
            # ¿Existe al menos 1 cirujano viable?
            k_validos = [k for k in cirujanos if (ci, k) in ck and all((k, tau) in dk for tau in bloques)]
            if not k_validos: continue
                
            # ¿Existe al menos 1 anestesista viable?
            m_validos = [m for m in anestesistas if (ci, m) in cm and all((m, tau) in dm for tau in bloques)]
            if not m_validos: continue

            for p in pabellones:
                if all((p, tau) in dp for tau in bloques):
                    ZI_keys.append((i, t, p))
                    Y_keys.extend((i, t, p, k) for k in k_validos)
                    H_keys.extend((i, t, p, m) for m in m_validos)

    ZI = model.addVars(ZI_keys, vtype=GRB.BINARY, name="ZI")
    Y  = model.addVars(Y_keys,  vtype=GRB.BINARY, name="Y")
    H  = model.addVars(H_keys,  vtype=GRB.BINARY, name="H")

    # 🔑 PASO 2: Variables derivadas (solo para ZI válidos)
    Z_keys = set()
    LQ_keys = set()
    WI_keys = set()
    W_keys = set()
    
    for i, t0, p in ZI_keys:
        d = d_cir[ci_paciente[i]]
        r = r_rec[ci_paciente[i]]
        t_rec = t0 + d
        
        # Z
        Z_keys.update((i, tau, p) for tau in range(t0, t0 + d))
        # LQ
        LQ_keys.update((i, tau, p) for tau in range(t0 + d, min(t0 + d + limpieza, T_MAX + 1)))
        # WI (solo si hay tiempo de recuperación válido)
        if t_rec <= T_MAX:
            for c in camas:
                WI_keys.add((i, t_rec, c))
                W_keys.update((i, tau, c) for tau in range(t_rec, min(t_rec + r, T_MAX + 1)))
            
    Z  = model.addVars(Z_keys,  vtype=GRB.BINARY, name="Z")
    LQ = model.addVars(LQ_keys, vtype=GRB.BINARY, name="LQ")
    WI = model.addVars(WI_keys, vtype=GRB.BINARY, name="WI")
    W  = model.addVars(W_keys,  vtype=GRB.BINARY, name="W")
    
    O = model.addVars(pabellones, tiempos, vtype=GRB.BINARY, name="O")

    return X, ZI, Z, LQ, WI, W, Y, H, O