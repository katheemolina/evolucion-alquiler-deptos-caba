# Análisis de la evolución del mercado de alquiler en CABA (2018–2026)

**Trabajo Final Integrador — Calidad y Visualización de Datos (UNSAdA)**  
Licenciatura en Informática — Prof. Mariana Adó
### Alumnos: 
- Giordano, Emilio
- Molina, Katherine
- Moscato, Agustín

> ¿Cómo evolucionaron los precios, la oferta y la accesibilidad salarial en el mercado de alquiler porteño?

---

## Estructura del repositorio

```
📁 escalas_salariales/
📁 datos_fuente_departamentos/
📄 dataset_maestro.csv
📄 dataset_barrios_mensual.csv
📄 integrar_datasets_alquiler.py
📄 perfilado_auxiliar.py
📄 generar_graficos_evidencia.py
📄 DOCUMENTACION_DATASETS.md
```

---

### 📁 `escalas_salariales/`

Contiene los archivos originales descargados de las escalas salariales del convenio colectivo 130/75 (Empleados de Comercio), categoría Administrativo A, desde 2018 hasta la actualidad. A partir de estos archivos se ejecutó el script de integración salarial que genera los datasets de salida:

- `dataset_mensual_administrativo_a.csv` — sueldo básico mensual con flag de interpolación en los meses sin escala publicada
- `dataset_trimestral_administrativo_a.csv` — promedio trimestral derivado del mensual, alineado con la frecuencia del dataset maestro

---

### 📁 `datos_fuente_departamentos/`

Contiene los 8 datasets originales descargados del Instituto de Estadística y Censos de la Ciudad de Buenos Aires (IDECBA), sin modificaciones:

- **3 archivos de precio promedio de publicación (pesos)** de departamentos en alquiler usados, por comuna, para 1, 2 y 3 ambientes — frecuencia trimestral, desde 2018
- **3 archivos de superficie total (m²)** de departamentos publicados en alquiler por barrio, para 1, 2 y 3 ambientes — frecuencia mensual, desde 2013
- **1 archivo de superficie promedio (m²)** por cantidad de ambientes a nivel ciudad — frecuencia mensual, desde 2010
- **1 archivo de equivalencia barrio ↔ comuna** — tabla auxiliar utilizada para integrar fuentes con distinta granularidad geográfica

Estos archivos fueron la base del proceso de integración, limpieza y transformación documentado en el informe final.

---

### 📄 Archivos en el directorio principal

Los archivos en el main son los **datasets limpios y transformados** resultantes del proceso completo, listos para el análisis y la construcción del dashboard:

| Archivo | Descripción |
|---------|-------------|
| `dataset_maestro.csv` | Dataset integrado por comuna × trimestre × ambientes (desde 2018-Q1). Incluye precios, superficie, cantidad estimada de departamentos y ratios de accesibilidad salarial |
| `dataset_barrios_mensual.csv` | Dataset mensual por barrio con superficie total, departamentos estimados y sueldo de referencia |
| `integrar_datasets_alquiler.py` | Script principal de integración y transformación  |
| `perfilado_auxiliar.py` | Script de perfilado: métricas de calidad, completitud y distribución |
| `generar_graficos_evidencia.py` | Generación de gráficos para el informe |
| `DOCUMENTACION_DATASETS.md` | Documentación de fuentes, supuestos metodológicos y decisiones de integración |

---

## Fuentes de datos

- [IDECBA — Banco de Datos Mercado Inmobiliario](https://www.estadisticaciudad.gob.ar/eyc/categoria-banco-datos/mercado-inmobiliario/)
- [Buenos Aires Data — Barrios](https://data.buenosaires.gob.ar/dataset/barrios)
- Convenio colectivo 130/75 — Empleados de Comercio, categoría Administrativo A
