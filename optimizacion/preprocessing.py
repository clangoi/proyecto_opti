from optimizacion.utils import positivos_2d

def construir_ci_paciente(G):
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


def preparar_prefiltering(pacientes, G, DispP, DispK, DispM, Q, A):
    ci_paciente = construir_ci_paciente(G)
    validar_ci_paciente(pacientes, ci_paciente)

    return {
        "ci_paciente": ci_paciente,
        "DispP_pos": positivos_2d(DispP),
        "DispK_pos": positivos_2d(DispK),
        "DispM_pos": positivos_2d(DispM),
        "CK_pos": positivos_2d(Q),
        "CM_pos": positivos_2d(A),
    }