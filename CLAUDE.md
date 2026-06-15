# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Proyecto académico en español (UNSAdA — Calidad y Visualización de Datos). El código, los comentarios y la documentación están en español; mantené ese idioma al escribir código, commits y respuestas.

## Qué es

Pipeline de integración de datos (no es una app): toma archivos crudos del mercado de alquiler de CABA (IDECBA/GCBA) más escalas salariales del gremio de Comercio y produce datasets limpios para analizar la accesibilidad al alquiler. El entregable final son los CSV de salida y el informe de calidad, no un servicio.

## Comandos

Dependencias (no hay `requirements.txt`):
```powershell
pip install pandas numpy openpyxl xlrd
```
`openpyxl` lee `.xlsx`; `xlrd` es necesario para los `.xls` antiguos de `escalas_salariales/`.

Pipeline completo (el orden importa — ver dependencias abajo):
```powershell
# 1. Regenerar CSV de sueldos desde los 41 archivos fuente (xls/xlsx/pdf/jpg)
python escalas_salariales/extraer_escalas.py

# 2. Integración principal -> dataset_maestro.csv + dataset_barrios_mensual.csv
python integrar_datasets_alquiler.py

# 3. Perfilado / métricas de calidad para el informe (corré desde la raíz del repo)
python perfilado_auxiliar.py
```

No hay tests, linter ni build. La verificación es el **reporte de calidad** que imprime `integrar_datasets_alquiler.py` al final (shape, % de NaN por columna, rango temporal, barrios sin match, ratios alquiler/sueldo). Tras un cambio, compará esas métricas contra `docu/informe_calidad_datos.md`.

## Dependencias entre scripts (orden y rutas — fácil de romper)

- `extraer_escalas.py` usa `BASE_DIR = carpeta del script`, así que **escribe los CSV de sueldos dentro de `escalas_salariales/`**. En cambio `integrar_datasets_alquiler.py` los lee desde la **raíz del repo** (`dataset_trimestral_administrativo_a.csv`, `dataset_mensual_administrativo_a.csv`). Si regenerás los sueldos, hay que **copiar esos dos CSV a la raíz** antes de correr la integración.
- `perfilado_auxiliar.py` abre los CSV con rutas relativas (`"dataset_maestro.csv"`): hay que ejecutarlo **desde la raíz del repo**, no con `cd` adentro de otra carpeta.
- Los `.xlsx` de origen se localizan por **prefijo numérico** (`encontrar_archivo("13_")`, etc.), no por nombre completo. Por eso los nombres larguísimos del GCBA pueden cambiar sin romper el script — pero **no renombres los prefijos** `02_ 03_ 04_ 07_ 11_ 12_ 13_` ni `barrios_comunas...`.

## Arquitectura del pipeline de integración (`integrar_datasets_alquiler.py`)

Orquestado en `main()` como 8 pasos. La idea central es **alinear tres granularidades distintas** (precio por comuna/trimestre, superficie por barrio/mes, superficie promedio por ciudad/mes) y cruzarlas con el sueldo:

- **Grupo A — precios** (archivos `11_/12_/13_`): precio promedio por **comuna × trimestre × ambientes**. Formato wide→long con encabezados temporales reconstruidos (años mergeados en fila 1, trimestres en fila 2).
- **Grupo B — superficie** (`02_/03_/04_`): superficie total m² por **barrio × mes × ambientes**.
- **Superficie promedio** (`07_`): m² promedio por **ciudad × mes × ambientes**. Se usa como denominador para **estimar cantidad de deptos** = superficie_total / superficie_promedio (supuesto explícito: distribución de tamaños homogénea entre barrios).
- **Tabla barrio↔comuna**: puente para subir la superficie de barrio a nivel comuna y poder cruzarla con los precios.

Dos salidas:
- `dataset_maestro.csv` — comuna × trimestre × ambientes, desde `2018-Q1` (constante `PERIODO_INICIO_MAESTRO`; antes de esa fecha solo había superficie sin precio y se descarta). Incluye `ratio_alquiler_sueldo_pct` y `meses_sueldo_para_alquiler`.
- `dataset_barrios_mensual.csv` — barrio × mes, con superficie, cantidad estimada y sueldo de contexto.

Los joins son `outer`/`left` a propósito: **nunca se eliminan filas sin match**, quedan como NaN y se reportan en el paso de calidad.

### Problemas de calidad codificados (el corazón del trabajo)

Las funciones utilitarias resuelven defectos concretos de la fuente, numerados en los docstrings (`#1`–`#7`). Si tocás el parsing, preservá estos manejos:
1. `///` en precios = dato no disponible → `NaN` (`es_valor_faltante_gcba`).
2. Encoding roto de barrios, ej. `NUÃ'EZ` → `Núñez` (`corregir_encoding_barrio`).
3. `*` al final de un período = dato provisorio → flag `provisorio` (`parsear_trimestre`).
4. Precios por comuna vs. superficie por barrio → join barrio→comuna + suma.
5. Precios trimestrales vs. superficie mensual → derivar `periodo_trim` desde el mes.
6. Superficie promedio solo a nivel ciudad → supuesto de homogeneidad para estimar volumen.
7. Variantes de nombre de barrio (acentos, `Montserrat`/`Monserrat`, `La Paternal`/`Paternal`) → clave canónica sin acentos + `ALIAS_BARRIOS` (`clave_barrio`).

## Extracción de sueldos (`escalas_salariales/extraer_escalas.py`)

Heurística tolerante a 41 archivos de formatos heterogéneos (planillas verticales por mes, horizontales por trimestre, bloques históricos, nombres de archivo que codifican el rango de meses). Solo extrae la categoría **Administrativo A**, columna **Básico** (sin sumas no remunerativas). Detalles a respetar:
- `DATOS_MANUALES` contiene 7 valores de 2018 que vienen de PDF/JPG escaneados que el parser no puede leer; no los borres.
- Los huecos se completan con **interpolación lineal** y se marcan `interpolado=True` / `archivo=(interpolado)`.
- Filtro de ruido: valores `<= 500` se descartan; un básico que salta `>18%` respecto del anterior se trata como "total con no remunerativos" y se reemplaza por el último básico válido.

## Notas de entorno (Windows)

- Varios `.xlsx` de `datos_fuente_departamentos/` superan el límite de 260 caracteres de Windows. El repo **requiere `git config core.longpaths true`** (ya configurado global en esta máquina) o el `checkout` falla con "Filename too long".
