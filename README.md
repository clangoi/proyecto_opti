## `README.md`

````markdown
# Modelo de Programación con Gurobi

Este proyecto implementa un modelo de optimización para la programación de cirugías usando Python y Gurobi.

El modelo considera pacientes, pabellones, bloques de tiempo, camas de recuperación, cirujanos, anestesistas, especialidades médicas y disponibilidad de recursos.

---

## Estructura del proyecto

```text
proyecto_opti/
├── main.py
├── conjuntos.py
├── parametros.py
├── variables.py
├── funcion_objetivo.py
├── requirements.txt
├── README.md
└── restricciones/
    ├── __init__.py
    ├── restricciones.py
    ├── validaciones.py
    ├── restricciones_basicas.py
    ├── restricciones_pabellones.py
    ├── restricciones_personal.py
    └── restricciones_recuperacion.py
````

---

## Descripción de archivos

### `main.py`

Es el archivo principal del proyecto.

Se encarga de:

* Crear el modelo de Gurobi.
* Importar conjuntos, parámetros, variables, restricciones y función objetivo.
* Ejecutar la optimización.
* Mostrar los resultados.
* Guardar el modelo y la solución.

Este es el archivo que se debe ejecutar.

```bash
python main.py
```

---

### `conjuntos.py`

Define los conjuntos del modelo, por ejemplo:

* Pacientes.
* Bloques de tiempo.
* Pabellones.
* Camas de recuperación.
* Cirujanos.
* Anestesistas.
* Especialidades.
* Tipos de cirugía.

Este archivo puede leer los tamaños de los conjuntos desde archivos CSV.

---

### `parametros.py`

Carga y define los parámetros del modelo.

Algunos parámetros considerados son:

* Duración de cirugías.
* Duración de recuperación.
* Tiempo de limpieza de pabellones.
* Prioridad de pacientes.
* Compatibilidad cirugía-especialidad.
* Compatibilidad cirugía-cirujano.
* Compatibilidad cirugía-anestesista.
* Compatibilidad pabellón-especialidad.
* Disponibilidad de pabellones.
* Disponibilidad de cirujanos.
* Disponibilidad de anestesistas.

Los valores reales de estos parámetros deben ser cargados desde archivos CSV.

---

### `variables.py`

Define las variables de decisión del modelo.

Variables principales:

* `X[i]`: indica si el paciente `i` es operado.
* `ZI[i,t,p]`: indica si el paciente `i` inicia cirugía en el tiempo `t` en el pabellón `p`.
* `Z[i,t,p]`: indica si el paciente `i` ocupa el pabellón `p` en el tiempo `t`.
* `LQ[i,t,p]`: indica si el pabellón `p` está en limpieza luego de operar al paciente `i`.
* `WI[i,t,c]`: indica si el paciente `i` inicia recuperación en la cama `c`.
* `W[i,t,c]`: indica si el paciente `i` ocupa la cama `c`.
* `Y[i,t,p,k]`: indica si el cirujano `k` es asignado al paciente `i`.
* `H[i,t,p,m]`: indica si el anestesista `m` es asignado al paciente `i`.
* `O[p,t]`: indica si el pabellón `p` está ocioso en el tiempo `t`.

---

### `funcion_objetivo.py`

Define la función objetivo del modelo.

La función objetivo maximiza la prioridad de los pacientes operados y penaliza la ociosidad de los pabellones.

Forma general:

```text
max sum_i w[i] X[i] - alpha sum_p sum_t O[p,t]
```

---

## Carpeta `restricciones/`

Esta carpeta contiene las restricciones del modelo divididas en archivos más pequeños para facilitar el mantenimiento.

### `restricciones/__init__.py`

Permite importar la función principal de restricciones directamente desde la carpeta.

Ejemplo:

```python
from restricciones import agregar_restricciones
```

---

### `restricciones/restricciones.py`

Archivo coordinador de restricciones.

Este archivo llama internamente a los módulos de restricciones más pequeños.

---

### `restricciones/validaciones.py`

Contiene validaciones previas del modelo.

Por ejemplo:

* Cada paciente debe tener exactamente una cirugía asignada.
* Las duraciones de cirugía deben ser enteras positivas.
* Las duraciones de recuperación deben ser enteras positivas.
* Los tiempos de limpieza deben ser enteros no negativos.

---

### `restricciones/restricciones_basicas.py`

Contiene restricciones generales del modelo, como:

* Relación entre paciente operado e inicio de cirugía.
* Compatibilidad entre cirugía, especialidad y pabellón.
* Ventanas temporales de inicio de cirugía.

---

### `restricciones/restricciones_pabellones.py`

Contiene restricciones asociadas a pabellones, como:

* Ocupación del pabellón.
* Limpieza del pabellón.
* Capacidad del pabellón.
* Disponibilidad del pabellón.
* Ociosidad del pabellón.

---

### `restricciones/restricciones_personal.py`

Contiene restricciones asociadas al personal médico, como:

* Asignación de cirujanos.
* Compatibilidad de cirujanos.
* Disponibilidad real de cirujanos bloque a bloque.
* Asignación de anestesistas.
* Compatibilidad de anestesistas.
* Disponibilidad real de anestesistas bloque a bloque.

---

### `restricciones/restricciones_recuperacion.py`

Contiene restricciones asociadas a recuperación, como:

* Inicio de recuperación posterior a cirugía.
* Ocupación de camas.
* Capacidad de camas.
* Restricción de que un paciente no ocupe más de una cama al mismo tiempo.
* Límite del horizonte considerando cirugía y recuperación.

---

## Supuestos actuales del modelo

El modelo está formulado bajo el supuesto de que:

```text
Cada paciente puede tener solo una cirugía.
```

Por eso las variables están indexadas por paciente, tiempo y recurso, pero no por tipo de cirugía.

Por ejemplo:

```python
ZI[i, t, p]
```

y no:

```python
ZI[i, ci, t, p]
```

Si en el futuro se permite que un paciente tenga más de una cirugía, será necesario agregar el índice `ci` a varias variables y restricciones.

---

## Instalación

Se recomienda usar un entorno virtual.

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual

En Windows:

```bash
venv\Scripts\activate
```

En macOS o Linux:

```bash
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Requisitos importantes

Este proyecto requiere tener instalado Gurobi y una licencia válida.

Para verificar que Gurobi funciona correctamente, ejecutar:

```bash
python -c "import gurobipy as gp; print(gp.gurobi.version())"
```

Si aparece la versión de Gurobi, la instalación está funcionando.

---

## Ejecución del modelo

Para ejecutar el modelo:

```bash
python main.py
```

Al finalizar, el programa puede generar archivos como:

```text
modelo_programacion_quirurgica.lp
solucion_programacion_quirurgica.sol
```

El archivo `.lp` contiene la formulación matemática exportada.

El archivo `.sol` contiene la solución encontrada por Gurobi, si existe una solución factible.

---

## Datos de entrada

Los datos del modelo deben estar definidos en archivos CSV y ser cargados desde `parametros.py` y `conjuntos.py`.

Ejemplos de archivos esperados:

```text
data/
├── parametros_globales.csv
├── paciente_cirugia.csv
├── parametros_cirugia.csv
├── limpieza_pabellones.csv
├── prioridad_pacientes.csv
├── especialidad_cirugia.csv
├── cirujano_cirugia.csv
├── anestesista_cirugia.csv
├── pabellon_especialidad.csv
├── disponibilidad_pabellones.csv
├── disponibilidad_cirujanos.csv
└── disponibilidad_anestesistas.csv
```

---

## Recomendaciones

Antes de ejecutar el modelo, verificar que:

1. Cada paciente tenga exactamente una cirugía asignada.
2. Las duraciones de cirugía sean enteras positivas.
3. Las duraciones de recuperación sean enteras positivas.
4. Los tiempos de limpieza sean enteros no negativos.
5. Las disponibilidades estén definidas para todos los recursos y bloques de tiempo.
6. Los archivos CSV tengan los nombres de columnas esperados por `parametros.py`.

---

## Ejecución rápida

```bash
pip install -r requirements.txt
python main.py
```

```
```
