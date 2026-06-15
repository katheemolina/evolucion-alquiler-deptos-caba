# Documentación de datasets — Sueldo básico Administrativo A (Empleados de Comercio)

## Selección de los datasets

Para armar el **dataset mensual** y el **dataset trimestral** de sueldos básicos de la categoría **Administrativo A** del convenio de Empleados de Comercio, se descargaron y procesaron **41 archivos** provenientes del Sindicato de Empleados de Comercio de La Plata (SEC La Plata):

| Tipo de archivo | Cantidad |
|-----------------|----------|
| Excel (.xls / .xlsx) | 35 |
| PDF escaneados | 4 |
| Imágenes (.jpg) | 2 |
| **Total** | **41** |

De esos archivos se extrajo, para cada mes disponible, el **año**, el **mes** y el **valor del sueldo básico** de **Administrativo A** expresado en **pesos argentinos ($ ARS)**.

La fuente institucional de referencia es la página oficial de escalas salariales del sindicato:

**[Escala Salarial — SEC La Plata](https://www.seclaplata.org.ar/gremiales/escalasalarial)**

Convenio Colectivo de Trabajo **130/75** — Empleados de Comercio.

### Proceso de construcción

1. **Extracción automática** mediante el script `extraer_escalas.py`, que interpreta distintos formatos de planillas (tablas por mes, tablas horizontales por trimestre, archivos históricos en PDF e imágenes).
2. **Consolidación mensual**: un registro por mes, priorizando el archivo más reciente o específico cuando hay superposición.
3. **Interpolación lineal** de **9 meses** sin dato directo en los archivos, para completar la serie entre **enero 2018** y julio 2026. Esos registros quedan marcados con `interpolado = True` y fuente `(interpolado)`.
4. **Agregación trimestral**: promedio aritmético del básico mensual por año y trimestre (Q1–Q4).

> **Nota:** Los datos de 2017 fueron excluidos del análisis. La serie comienza en **enero 2018**.

### Archivos de salida

| Archivo | Registros | Descripción |
|---------|-----------|-------------|
| `dataset_mensual_administrativo_a.csv` | 103 | Serie mensual completa (94 observaciones reales + 9 interpoladas) |
| `dataset_trimestral_administrativo_a.csv` | 35 | Promedio trimestral del básico (2018 Q1 – 2026 Q3) |

**Período cubierto:** enero 2018 – julio 2026.

---

## Dataset 1 — Mensual

**Nombre:**  
`dataset_mensual_administrativo_a.csv` — Sueldo básico mensual de Administrativo A (Empleados de Comercio, SEC La Plata)

**Fuente:**  
Escalas salariales oficiales del Sindicato de Empleados de Comercio de La Plata (SEC La Plata), disponibles en [https://www.seclaplata.org.ar/gremiales/escalasalarial](https://www.seclaplata.org.ar/gremiales/escalasalarial), complementadas con archivos descargados de esa misma fuente (planillas Excel, PDF e imágenes de escalas históricas).

**Fecha de obtención:**  
15/06/2026

**Temática general:**  
Evolución del **sueldo básico** de la categoría **Administrativo A** del convenio colectivo 130/75 (Empleados de Comercio), en pesos argentinos, desagregado por mes.

**Contexto de uso:**  
Este dataset se incorporó como **variable contextual de ingresos formales del sector comercio** en un análisis de **alquiler de departamentos en la Ciudad Autónoma de Buenos Aires (CABA)**. Permite contrastar la evolución del poder adquisitivo nominal y real de un perfil salarial representativo (administrativo de comercio) frente a la dinámica de precios de alquiler, enriqueciendo el **dashboard**, el **análisis exploratorio** y el **storytelling** del trabajo con una dimensión laboral y gremial que no está presente en las bases de alquileres en sí mismas. Facilita calcular ratios aproximados (ej. meses de sueldo básico necesarios para cubrir un alquiler) y observar tendencias trimestrales o anuales alineadas con el mercado inmobiliario.

**Variables principales:**

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `anio` | entero | Año calendario |
| `mes` | entero | Mes (1–12) |
| `fecha` | fecha | Primer día del mes (YYYY-MM-DD) |
| `trimestre` | texto | Trimestre calendario (Q1–Q4) |
| `basico` | numérico | Sueldo básico Administrativo A en $ ARS |
| `interpolado` | booleano | `True` si el valor fue estimado por interpolación lineal |
| `archivo` | texto | Archivo fuente o `(interpolado)` |

**Meses interpolados (sin escala directa en los archivos):**  
2018-09, 2018-11, 2018-12, 2019-04, 2019-11, 2019-12, 2020-11, 2020-12, 2023-01.

---

## Dataset 2 — Trimestral

**Nombre:**  
`dataset_trimestral_administrativo_a.csv` — Promedio trimestral del sueldo básico de Administrativo A (Empleados de Comercio, SEC La Plata)

**Fuente:**  
Derivado del dataset mensual (`dataset_mensual_administrativo_a.csv`), cuyos datos originales provienen de las escalas salariales del SEC La Plata ([enlace oficial](https://www.seclaplata.org.ar/gremiales/escalasalarial)).

**Fecha de obtención:**  
15/06/2026

**Temática general:**  
**Promedio trimestral** del sueldo básico de **Administrativo A** (convenio 130/75, Empleados de Comercio), en pesos argentinos, para los trimestres Q1 a Q4 de cada año entre **2018** y 2026.

**Contexto de uso:**  
Se construyó para **alinear la frecuencia temporal** del análisis de alquileres en CABA con indicadores macro y de mercado que suelen reportarse por trimestre. En el dashboard y la narrativa del trabajo permite comparar de forma más estable la evolución salarial frente a la de alquileres (también agregables por trimestre), reducir el ruido mensual propio de los acuerdos paritarios y sostener visualizaciones y conclusiones de **contexto socioeconómico** — por ejemplo, si el alquiler medio en una zona crece más rápido que el básico de comercio en el mismo período.

**Variables principales:**

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `anio` | entero | Año calendario |
| `trimestre` | texto | Trimestre (Q1, Q2, Q3, Q4) |
| `basico_promedio` | numérico | Promedio del básico mensual del trimestre ($ ARS) |
| `meses_incluidos` | lista | Meses que componen el promedio |
| `n_meses` | entero | Cantidad de meses promediados (3 en series completas) |

**Metodología de agregación:**  
`basico_promedio = promedio(básico mensual de los meses del trimestre)`. Tras la interpolación mensual, todos los trimestres del período cuentan con 3 meses, salvo el último trimestre parcial disponible (2026 Q3, con 1 mes: julio).

---

## Consideraciones metodológicas

- **Categoría seleccionada:** solo **Administrativo A** y su columna **Básico**, sin sumas no remunerativas, presentismo ni antigüedad.
- **Alcance geográfico del sindicato:** La Plata y ámbito del SEC; se utiliza como **proxy de ingreso formal del sector comercio** en el análisis de CABA por ser una referencia gremial amplia y publicada.
- **Limitaciones:** los valores interpolados son estimaciones lineales entre meses conocidos; no reemplazan escalas oficiales faltantes. Para análisis de poder adquisitivo real conviene deflactar con IPC u otro índice.
- **Reproducibilidad:** ejecutar `python extraer_escalas.py` en la carpeta de escalas regenera ambos CSV a partir de los archivos fuente.

---

## Ejemplo de uso en el análisis de alquileres (CABA)

| Aplicación | Descripción |
|------------|-------------|
| Variable contextual | Incorporar evolución salarial al relato del mercado de alquiler |
| Ratios | Alquiler medio ÷ básico Administrativo A ≈ “meses de sueldo básico” |
| Series temporales | Gráficos duales alquiler (CABA) vs. básico comercio (mensual o trimestral) |
| Dashboard | KPIs de contexto: variación % trimestral del básico, último valor vigente |
| Storytelling | Vincular acuerdos salariales y tensiones de accesibilidad habitacional |

---

*Documentación generada el 15/06/2026 — Proyecto: análisis de alquiler de departamentos en CABA.*
