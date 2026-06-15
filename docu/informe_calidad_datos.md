# Del dato crudo al dato confiable: Mercado de alquiler de departamentos en CABA

**Trabajo Final Integrador — Calidad y Visualización de Datos**  
**Licenciatura en Informática**

---

## 1. Selección de los datasets

### 1.1 Precio promedio de publicación por comuna (1, 2 y 3 ambientes)

| Campo | Detalle |
|-------|---------|
| **Nombre** | Precio promedio de publicación (pesos) de departamentos en alquiler usados por comuna (1, 2 y 3 ambientes) |
| **Fuente** | Instituto de Estadística y Censos de la Ciudad de Buenos Aires (IDECBA), [Banco de Datos — Mercado inmobiliario](https://www.estadisticaciudad.gob.ar/eyc/categoria-banco-datos/mercado-inmobiliario/) |
| **Fecha de obtención** | 09/06/2026 |
| **Temática general** | Mercado inmobiliario (alquiler): CABA |
| **Contexto de uso** | Medir la evolución trimestral del precio de publicación de alquileres según tamaño del departamento y ubicación administrativa (comuna). Base Argenprop. Solo comunas con muestra mínima de ofertas. |

### 1.2 Superficie total publicada en alquiler por barrio (1, 2 y 3 ambientes)

| Campo | Detalle |
|-------|---------|
| **Nombre** | Superficie total (m²) de departamentos publicados en alquiler (usados y a estrenar) por barrio |
| **Fuente** | IDECBA (misma fuente anterior) |
| **Fecha de obtención** | 09/06/2026 |
| **Temática general** | Mercado inmobiliario (alquiler): CABA |
| **Contexto de uso** | Cuantificar el volumen de oferta (en metros cuadrados) publicada mensualmente por barrio. Permite analizar dinámica espacial de la oferta. Series con cambio de proveedor (Adinco → Argenprop) en 2015. |

### 1.3 Superficie promedio por cantidad de ambientes (nivel ciudad)

| Campo | Detalle |
|-------|---------|
| **Nombre** | Superficie promedio (m²) de departamentos publicados en alquiler por cantidad de ambientes |
| **Fuente** | IDECBA (misma fuente anterior) |
| **Fecha de obtención** | 09/06/2026 |
| **Temática general** | Mercado inmobiliario (alquiler): CABA |
| **Contexto de uso** | Indicador mensual a nivel ciudad para estimar cantidad de unidades a partir de superficie total. Sin desagregación geográfica. |

### 1.4 Tabla de equivalencia barrio ↔ comuna

| Campo | Detalle |
|-------|---------|
| **Nombre** | Barrios por Comuna (archivo curso Ciencia de Datos y Políticas Públicas) |
| **Fuente** | [Buenos Aires Data — Dataset Barrios](https://data.buenosaires.gob.ar/dataset/barrios) |
| **Fecha de obtención** | 09/06/2026 |
| **Temática general** | División territorial / infraestructura |
| **Contexto de uso** | Tabla auxiliar para asignar cada barrio a su comuna (1–15) y habilitar la integración entre datasets con distinta granularidad geográfica. |

### 1.5 Sueldo básico mensual — Administrativo A (Empleados de Comercio)

| Campo | Detalle |
|-------|---------|
| **Nombre** | `dataset_mensual_administrativo_a.csv` |
| **Fuente** | [Escalas salariales SEC La Plata](https://www.seclaplata.org.ar/gremiales/escalasalarial) — Convenio 130/75, categoría Administrativo A (solo básico) |
| **Fecha de obtención** | 15/06/2026 |
| **Temática general** | Salarios formales del sector comercio |
| **Contexto de uso** | Variable contextual de ingreso para enriquecer el dataset barrios mensual y calcular ratios de accesibilidad. Incluye flag `sueldo_interpolado` en 9 meses sin escala directa. |

### 1.6 Sueldo básico trimestral — Administrativo A (derivado)

| Campo | Detalle |
|-------|---------|
| **Nombre** | `dataset_trimestral_administrativo_a.csv` |
| **Fuente** | Derivado del mensual (documentado en `DOCUMENTACION_DATASETS.md`) |
| **Fecha de obtención** | 15/06/2026 |
| **Temática general** | Salarios formales del sector comercio (promedio trimestral) |
| **Contexto de uso** | Alinear frecuencia temporal con el maestro de alquileres (trimestral) y calcular `ratio_alquiler_sueldo_pct` y `meses_sueldo_para_alquiler`. Proxy sectorial, no desagregado por comuna. |

---

## 2. Exploración de metadatos

A continuación se documentan las variables de los datasets integrados (salida del pipeline) y de las fuentes auxiliares que intervienen en la construcción del maestro. Para cada variable se indica su **significado**, **tipo de dato** en el sistema y **clasificación** según la tipología de la asignatura: **Identificador**, **Numérica**, **Ordinal** o **Categórica**.

> **Criterio de clasificación:** las variables temporales (`periodo`, `periodo_trim`) se clasifican como **Ordinal** por tener un orden natural. Los códigos geográficos (`comuna`, `barrio`) son **Identificador** (y además admiten lectura categórica en visualizaciones). Las magnitudes medibles en pesos o m² son **Numérica**. Los flags y etiquetas sin orden intrínseco (`provisorio`, `interpolado`) son **Categórica**. La cantidad de ambientes (1, 2, 3) es **Ordinal** por reflejar un orden de tamaño del inmueble.

### 2.1 Dataset maestro integrado (`dataset_maestro.csv`)

Dataset principal de análisis: comuna × trimestre × ambientes, desde 2018-Q1.

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `comuna` | Número de comuna de la CABA (1 a 15) | Entero | Identificador |
| `periodo_trim` | Trimestre calendario de referencia (formato `YYYY-QN`, ej. `2018-Q1`) | Texto | Ordinal |
| `ambientes` | Cantidad de ambientes del departamento ofrecido (1, 2 o 3) | Entero | Ordinal |
| `precio_promedio_pesos` | Precio promedio de publicación del alquiler en pesos argentinos ($ ARS), según IDECBA/Argenprop | Float | Numérica |
| `provisorio` | Indica si el precio fue marcado con asterisco (*) como dato provisorio en la fuente | Booleano | Categórica |
| `sueldo_basico_admin_a` | Promedio trimestral del sueldo básico de la categoría Administrativo A (Empleados de Comercio, SEC La Plata) | Float | Numérica |
| `n_meses_sueldo` | Cantidad de meses salariales incluidos en el promedio trimestral (3 salvo trimestre parcial) | Entero | Numérica |
| `ratio_alquiler_sueldo_pct` | Porcentaje del sueldo básico que representa el alquiler: `(precio / sueldo) × 100` | Float | Numérica |
| `meses_sueldo_para_alquiler` | Meses de sueldo básico equivalentes al monto del alquiler: `precio / sueldo` | Float | Numérica |
| `superficie_total_m2` | Metros cuadrados totales publicados en alquiler en la comuna (suma agregada desde barrios) | Float | Numérica |
| `cantidad_deptos_estimada` | Cantidad estimada de departamentos en oferta: `superficie_total_m2 / superficie_promedio_m2` (promedio a nivel ciudad) | Float | Numérica |

### 2.2 Dataset barrios mensual (`dataset_barrios_mensual.csv`)

Dataset de apoyo para visualizaciones espaciales y series mensuales de oferta.

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `barrio` | Nombre oficial del barrio de la CABA | Texto | Identificador |
| `periodo` | Mes calendario de referencia (formato `YYYY-MM`, ej. `2018-03`) | Texto | Ordinal |
| `ambientes` | Cantidad de ambientes del departamento (1, 2 o 3) | Entero | Ordinal |
| `superficie_total_m2` | Metros cuadrados publicados en alquiler en el barrio durante el mes | Float | Numérica |
| `superficie_promedio_m2` | Superficie promedio de departamentos en alquiler a nivel ciudad, usada como denominador para estimar unidades | Float | Numérica |
| `cantidad_deptos_estimada` | Unidades estimadas en oferta en el barrio: `superficie_total_m2 / superficie_promedio_m2` | Float | Numérica |
| `sueldo_basico_admin_a` | Sueldo básico mensual Administrativo A del mes correspondiente (contexto salarial) | Float | Numérica |
| `sueldo_interpolado` | Indica si el sueldo del mes fue estimado por interpolación lineal (sin escala oficial directa) | Booleano | Categórica |

### 2.3 Fuentes IDECBA — precios por comuna (Grupo A, formato long)

Variables obtenidas tras la lectura y transformación de los archivos 11, 12 y 13 (precio promedio por comuna y trimestre).

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `comuna` | Número de comuna (1 a 15); excluye fila agregada `Total` | Entero | Identificador |
| `periodo` | Trimestre calendario (`YYYY-QN`) reconstruido desde filas de año y trimestre del Excel | Texto | Ordinal |
| `ambientes` | Tipología del departamento según archivo fuente (1, 2 o 3 ambientes) | Entero | Ordinal |
| `precio_promedio_pesos` | Valor numérico del precio promedio de publicación; `///` se convierte en nulo | Float | Numérica |
| `provisorio` | Verdadero si el trimestre en el encabezado original tenía asterisco (*) | Booleano | Categórica |

### 2.4 Fuentes IDECBA — superficie total por barrio (Grupo B, formato long)

Variables obtenidas de los archivos 02, 03 y 04 (superficie publicada en alquiler por barrio y mes).

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `barrio` | Nombre del barrio; excluye fila agregada `Total` | Texto | Identificador |
| `periodo` | Mes calendario (`YYYY-MM`) reconstruido desde año y mes abreviado del Excel | Texto | Ordinal |
| `ambientes` | Tipología del departamento (1, 2 o 3 ambientes) | Entero | Ordinal |
| `superficie_total_m2` | Metros cuadrados en oferta en el barrio y mes; puede ser 0 si no hubo publicaciones | Float | Numérica |

### 2.5 Fuente IDECBA — superficie promedio por ambientes (archivo 07)

Indicador a nivel ciudad utilizado para estimar cantidad de departamentos.

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `periodo` | Mes calendario (`YYYY-MM`) | Texto | Ordinal |
| `ambientes` | Cantidad de ambientes (1, 2 o 3) | Entero | Ordinal |
| `superficie_promedio_m2` | Superficie promedio publicada en alquiler para esa tipología en la ciudad | Float | Numérica |
| `provisorio` | Verdadero si el mes en la fuente tenía asterisco (*) | Booleano | Categórica |

### 2.6 Tabla auxiliar barrios ↔ comunas

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `BARRIO` / `barrio` | Nombre del barrio en mayúsculas (fuente) o Title Case (integrado) | Texto | Identificador |
| `COMUNA` / `comuna` | Número de comuna a la que pertenece el barrio (1 a 15) | Entero | Identificador |

### 2.7 Sueldo básico mensual — Administrativo A (`dataset_mensual_administrativo_a.csv`)

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `anio` | Año calendario del registro salarial | Entero | Ordinal |
| `mes` | Mes calendario (1 a 12) | Entero | Ordinal |
| `fecha` | Primer día del mes (`YYYY-MM-DD`) | Fecha | Ordinal |
| `trimestre` | Trimestre calendario asociado (Q1, Q2, Q3, Q4) | Texto | Ordinal |
| `basico` | Sueldo básico de Administrativo A en pesos argentinos ($ ARS) | Float | Numérica |
| `interpolado` | Verdadero si el valor fue completado por interpolación lineal | Booleano | Categórica |
| `archivo` | Nombre del archivo fuente de la escala salarial o `(interpolado)` | Texto | Categórica |

### 2.8 Sueldo básico trimestral — Administrativo A (`dataset_trimestral_administrativo_a.csv`)

| Variable | Significado | Tipo de dato | Clasificación |
|----------|-------------|--------------|---------------|
| `anio` | Año calendario del trimestre | Entero | Ordinal |
| `trimestre` | Trimestre calendario (Q1, Q2, Q3, Q4) | Texto | Ordinal |
| `basico_promedio` | Promedio aritmético del básico mensual del trimestre ($ ARS) | Float | Numérica |
| `meses_incluidos` | Lista de meses (1–12) que componen el promedio | Texto / lista | Categórica |
| `n_meses` | Cantidad de meses promediados (3 en trimestres completos; 1 en 2026-Q3 parcial) | Entero | Numérica |

---

## 3. Perfilado de los datos (Data Profiling)

> **Evidencia técnica:** script de integración `integrar_datasets_alquiler.py`, script auxiliar `perfilado_auxiliar.py`, gráficos `evidencia_histograma_boxplot_precios.png` y `evidencia_serie_superficie.png`.

### 3.1 Análisis estructural

| Aspecto | Dataset maestro | Dataset barrios mensual |
|---------|-----------------|-------------------------|
| **Filas** | 1.530 | 22.176 |
| **Columnas** | 11 | 8 |
| **Granularidad temporal** | Trimestral (`2018-Q1` a `2026-Q2`) | Mensual (`2013-07` a `2026-04`) |
| **Granularidad espacial** | 15 comunas | 48 barrios |
| **Cardinalidad ambientes** | 3 valores (1, 2, 3) | 3 valores (1, 2, 3) |
| **Duplicados** en clave primaria lógica (`comuna`+`periodo_trim`+`ambientes`) | **0** | N/A (clave: `barrio`+`periodo`+`ambientes`) |
| **Formato fuente original** | Excel ancho (wide): años en fila 1, trimestres en fila 2 | Excel ancho: años + meses abreviados |
| **Formato integrado** | Long (una fila por observación) | Long |

**Observación estructural:** el join `outer` inicial producía 2.340 filas, pero 810 correspondían a 2013–2017 con superficie y sin precio (los precios del Grupo A comienzan en 2018-Q1). Se aplicó un **filtro desde `2018-Q1`** al maestro exportado, dejando 1.530 filas con cobertura conjunta precio + superficie. El dataset barrios mensual conserva el rango completo desde 2013 para análisis espaciales de oferta.

### 3.2 Análisis de completitud

**Dataset maestro — % de valores faltantes (NaN):**

| Variable | % NaN |
|----------|-------|
| `comuna` | 0,00 % |
| `periodo_trim` | 0,00 % |
| `ambientes` | 0,00 % |
| `precio_promedio_pesos` | **15,82 %** |
| `provisorio` | 2,94 % * |
| `superficie_total_m2` | 0,00 % |
| `cantidad_deptos_estimada` | 0,00 % |
| `ratio_alquiler_sueldo_pct` | 15,82 % * |
| `meses_sueldo_para_alquiler` | 15,82 % * |
| `sueldo_basico_admin_a` | 0,00 % |

\* El mismo % que precio: el ratio solo se calcula cuando hay precio y sueldo.

\* `provisorio` es NaN cuando no hay dato de precio (comunas con `///` en la fuente).

**% de precio faltante por comuna** (muestra insuficiente según IDECBA, período ≥ 2018-Q1):

| Comuna | % NaN precio |
|--------|--------------|
| 8 | **98,0 %** |
| 9 | 52,0 % |
| 4 | 36,3 % |
| 10 | 13,7 % |
| Resto (1–3, 5–7, 11–15) | 2,9 % – 4,9 % |

**Dataset barrios mensual:**
- Sin NaN en variables numéricas principales tras la integración.
- **3.846 observaciones** (17,3 %) con `superficie_total_m2 = 0` (sin publicaciones ese mes en ese barrio/tipología).

### 3.3 Análisis descriptivo y de distribución

**`precio_promedio_pesos`** (1.288 valores no nulos):

| Estadístico | Valor (ARS) |
|-------------|-------------|
| Media | 207.808 |
| Mediana | 53.751 |
| Desvío estándar | 269.728 |
| Mínimo | 6.044 |
| Máximo | 1.275.561 |
| P25 / P75 | 19.260 / 365.379 |

La fuerte diferencia entre media y mediana, junto con un máximo muy elevado, indica **cola derecha pronunciada** (comunas con precios altos y alta inflación en el período).

**`superficie_total_m2`** (comuna-trimestre, desde 2018-Q1):
- Media: 3.770 m² | Mediana: 2.600 m² | Máx.: 26.432 m²

**`cantidad_deptos_estimada`**:
- Media: 84,8 deptos | Mediana: 58,4 | Máx.: 629,7

**Ratio alquiler/sueldo (monoambiente, `ambientes = 1`, donde hay precio):**
- Mediana: **46,7 %** | Media: 50,1 % | Máximo: 108,2 %
- En 2018-Q1 comuna 1: alquiler 1 ambiente ≈ **39,8 %** del sueldo básico (0,40 meses de sueldo)

**Evidencia gráfica:**
- `evidencia_histograma_boxplot_precios.png`: histograma de precios y boxplot por cantidad de ambientes.
- `evidencia_serie_superficie.png`: serie temporal de superficie total publicada en la ciudad.

```python
# Fragmento de evidencia — estadísticas descriptivas
df["precio_promedio_pesos"].describe()
df.duplicated(subset=["comuna", "periodo_trim", "ambientes"]).sum()  # → 0
```

### 3.4 Detección de problemas de calidad

| Problema | Evidencia | Impacto |
|----------|-----------|---------|
| **Valores `///`** en precios | 242 celdas → NaN (15,82 % del maestro filtrado) | Pérdida de precio en comunas con pocas ofertas |
| **Períodos sin precio (2013–2017)** | 810 filas eliminadas del maestro | Resuelto con filtro desde `2018-Q1` |
| **Datos provisorios (*)** | 180 observaciones con `provisorio=True` | Requiere cautela en análisis recientes (2025–2026) |
| **Encoding roto en barrios** | `NUÃ'EZ` en tabla equivalencia; tildes inconsistentes entre archivos de superficie | Riesgo de join fallido → resuelto con normalización |
| **Nombres de barrio inconsistentes** | `Agronomia` vs `Agronomía`, `Montserrat` vs `Monserrat` | Duplicados espurios (50 barrios) → unificados a 48 |
| **Granularidad geográfica distinta** | Precios por comuna, superficie por barrio | Requiere agregación espacial |
| **Granularidad temporal distinta** | Precios trimestrales vs superficie mensual | Requiere agregación temporal |
| **Superficie promedio sin desagregación** | Archivo 07 es a nivel ciudad | Supuesto de homogeneidad para estimar cantidad de deptos |
| **Superficie = 0** | 3.846 filas en dataset barrios | No es error: indica ausencia de oferta publicada |
| **Atípicos en precio** | Máximo >> P75; inflación acumulada | No se eliminan; se documentan y se consideran en visualizaciones (escala log opcional) |
| **Sueldo interpolado** | 9 meses en serie mensual (5,8 % de filas barrios) | Documentar en dashboard; no imputar alquileres |
| **Proxy salarial** | SEC La Plata ≠ ingreso real del inquilino ni por comuna | Ratios son indicadores aproximados de accesibilidad |
| **Comuna 8 casi sin precios** | 98,0 % NaN | Limita análisis comparativo en esa comuna |

---

## 4. Limpieza y transformación de los datos

Todas las transformaciones están implementadas y comentadas en `integrar_datasets_alquiler.py`.

### Transformación 1: De formato ancho (wide) a largo (long) con reconstrucción temporal

- **Qué:** cada archivo Excel del GCBA tiene años en fila 1 (celdas mergeadas) y subperíodos (trimestres o meses) en fila 2. Se reconstruye el índice temporal y se aplica `melt` para obtener una fila por observación.
- **Por qué:** el formato wide dificulta el análisis, los joins y las visualizaciones; el formato long es estándar para series temporales multivariadas.
- **Evidencia:** Paso 1 y 2 del script; resultado: 1.485 registros de precios, 22.176 de superficie barrial.

```python
# Reconstrucción de encabezados temporales (años con forward-fill)
años = df_raw.iloc[fila_anios, col_inicio:].ffill()
# ...
periodo = f"{meta['anio']}-{sufijo_q}"  # ej: 2018-Q1
```

### Transformación 2: Tratamiento de valores faltantes y datos provisorios

- **Qué:** reemplazo de `///` por `NaN`; detección de asterisco en trimestres para columna booleana `provisorio`; exclusión de filas `Total` y notas al pie.
- **Por qué:** `///` no es un número válido sino un código de confidencialidad por muestra insuficiente (documentado por IDECBA). El asterisco distingue datos revisables.
- **Evidencia:** funciones `es_valor_faltante_gcba()` y `parsear_trimestre()`; 242 precios ausentes en el maestro filtrado (no imputados).

### Transformación 3: Normalización de barrios y cruce espacial-temporal

- **Qué:** (a) corrección de encoding `NUÃ'EZ` → `Núñez`; (b) alias (`Montserrat`→`Monserrat`, `La Paternal`→`Paternal`); (c) asignación de comuna; (d) derivación de `periodo_trim` desde mes; (e) agregación de superficie y deptos estimados a comuna-trimestre; (f) join con precios.
- **Por qué:** sin esta cadena no es posible integrar fuentes con distinta granularidad geográfica y temporal.
- **Evidencia:** Pasos 4–6; 0 barrios sin match tras normalización; 48 barrios únicos en salida.

```python
# Variable derivada (supuesto documentado)
cantidad_deptos_estimada = superficie_total_m2 / superficie_promedio_m2
```

### Transformación 4: Recorte temporal del dataset maestro desde 2018-Q1

- **Qué:** filtro `periodo_trim >= 2018-Q1` sobre el maestro tras el join, eliminando 810 filas anteriores a la disponibilidad de precios.
- **Por qué:** antes de 2018-Q1 solo existía superficie agregada; esas filas tenían precio siempre NaN y elevaban artificialmente el 44,96 % de faltantes sin aportar al análisis integrado precio + oferta.
- **Evidencia:** función `filtrar_maestro_desde_periodo()`; maestro pasa de 2.340 a **1.530 filas**; faltantes de precio bajan a **15,82 %**.

```python
PERIODO_INICIO_MAESTRO = "2018-Q1"
df_maestro = filtrar_maestro_desde_periodo(df_maestro, PERIODO_INICIO_MAESTRO)
```

### Transformación 5: Integración de sueldos y cálculo de accesibilidad

- **Qué:** join del maestro con `dataset_trimestral_administrativo_a.csv` por `periodo_trim`; join del dataset barrios con el mensual por `periodo`; cálculo de `ratio_alquiler_sueldo_pct` y `meses_sueldo_para_alquiler`.
- **Por qué:** permite responder la pregunta de análisis sobre qué proporción del sueldo básico de comercio representa el alquiler, usando una referencia salarial pública y alineada en el tiempo.
- **Evidencia:** Paso 7 del script; 100 % de filas del maestro con sueldo asignado; monoambiente mediana 46,7 % del sueldo básico.

```python
ratio_alquiler_sueldo_pct = (precio_promedio_pesos / sueldo_basico_admin_a) * 100
meses_sueldo_para_alquiler = precio_promedio_pesos / sueldo_basico_admin_a
```

### 4.1 Reglas de calidad

| Regla | Descripción | Implementación |
|-------|-------------|----------------|
| **R1 — Dominio comuna** | `comuna ∈ {1, 2, …, 15}` | Filtro al leer Grupo A; validación en agregación |
| **R2 — Dominio ambientes** | `ambientes ∈ {1, 2, 3}` | Asignación explícita por archivo fuente |
| **R3 — Precio positivo** | Si no es NaN, `precio_promedio_pesos > 0` | Cumplida: 0 valores ≤ 0 en maestro |
| **R4 — Superficie no negativa** | `superficie_total_m2 ≥ 0` | Cumplida; 0 = sin oferta |
| **R5 — Período trimestral válido** | Formato `YYYY-Q[1-4]` | Generado por función `trimestre_desde_mes()` |
| **R6 — Integridad referencial barrio→comuna** | Todo barrio del Grupo B debe existir en tabla equivalencia | Auditada; 0 sin match tras normalización |
| **R7 — No duplicar claves** | Una fila por (`comuna`, `periodo_trim`, `ambientes`) | 0 duplicados verificados |
| **R8 — Preservar ausencias** | No imputar `///`; conservar NaN donde corresponda | Valores `///` → NaN sin imputación |
| **R9 — Corte temporal maestro** | `periodo_trim >= 2018-Q1` | Alineado al inicio de la serie de precios |
| **R10 — Sueldo positivo** | Si no es NaN, `sueldo_basico_admin_a > 0` | Cumplida en maestro integrado |
| **R11 — Ratio solo con precio** | `ratio_alquiler_sueldo_pct` calculado iff precio y sueldo no nulos | Evita divisiones inválidas |

---

## 5. Formulación de preguntas de análisis

Las siguientes preguntas guían las visualizaciones y el dashboard del TFI:

1. **¿Cómo evolucionó el precio promedio de publicación de alquiler entre 2018 y 2026 según comuna y cantidad de ambientes, y qué comunas concentran los mayores incrementos?**  
   *Variables:* `precio_promedio_pesos`, `comuna`, `periodo_trim`, `ambientes`.  
   *Viz sugerida:* líneas por comuna (facetas por ambientes), mapa coroplético de último trimestre.

2. **¿Qué comunas y barrios concentran mayor superficie ofrecida en alquiler, y cómo se relaciona el volumen estimado de departamentos con el nivel de precios?**  
   *Variables:* `superficie_total_m2`, `cantidad_deptos_estimada`, `precio_promedio_pesos`.  
   *Viz sugerida:* scatter precio vs cantidad estimada por comuna; barras apiladas de superficie por barrio.

3. **¿Qué proporción del sueldo básico de un empleado de comercio (Administrativo A) representa el alquiler publicado según comuna, tipología y trimestre, y qué comunas superan un umbral de referencia (p. ej. 30 %)?**  
   *Variables:* `precio_promedio_pesos`, `sueldo_basico_admin_a`, `ratio_alquiler_sueldo_pct`, `meses_sueldo_para_alquiler`, `comuna`, `periodo_trim`, `ambientes`.  
   *Viz sugerida:* líneas del ratio por comuna (faceta monoambiente); mapa coroplético; línea de referencia al 30 %; evolución dual alquiler vs. sueldo.

---

## Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `integrar_datasets_alquiler.py` | Script principal comentado (evidencia técnica) |
| `dataset_maestro.csv` | Dataset integrado comuna × trimestre × ambientes (desde 2018-Q1, con ratios alquiler/sueldo) |
| `dataset_barrios_mensual.csv` | Superficie, deptos estimados y sueldo mensual por barrio |
| `dataset_trimestral_administrativo_a.csv` | Sueldo básico trimestral (entrada) |
| `dataset_mensual_administrativo_a.csv` | Sueldo básico mensual (entrada) |
| `DOCUMENTACION_DATASETS.md` | Documentación de fuentes y metodología salarial |
| `perfilado_auxiliar.py` | Métricas de perfilado reproducibles |
| `generar_graficos_evidencia.py` | Generación de gráficos para el informe |
| `evidencia_histograma_boxplot_precios.png` | Distribución de precios |
| `evidencia_serie_superficie.png` | Serie temporal de oferta |

---

## Ejecución

```bash
python integrar_datasets_alquiler.py
python perfilado_auxiliar.py
python generar_graficos_evidencia.py
```
