# Punto 8 — Dashboard interactivo

Dashboard web del TFI (Mercado de alquiler de departamentos en CABA, 2018–2026).
Responde a las 3 preguntas de análisis con KPIs y gráficos **dinámicos** (filtrables por
cantidad de ambientes, rango de años y comuna).

## Stack

React + TypeScript + Vite · Tailwind CSS + shadcn/ui · Recharts (gráficos) · d3-geo (mapa).

## Cómo correrlo

```bash
cd 8_dashboard
npm install      # solo la primera vez
npm run dev      # http://localhost:5173
```

`npm run build` genera la versión estática en `dist/` (para entregar o desplegar).

## Datos (sin modificar el dataset fuente)

El dashboard lee `dataset_maestro.csv` **tal cual**: la fecha se deriva en runtime
parseando `periodo_trim` ("2018-Q1"). El script `scripts/copy-data.cjs` copia de forma
**verbatim** el CSV y el GeoJSON de comunas a `public/data/` antes de cada `dev`/`build`
(`public/data` está en `.gitignore`; no se duplica el dataset en el repo).

- Datos de mercado y sueldos: `../dataset_maestro.csv` (IDECBA + SEC La Plata)
- Geometría de comunas: `../6_visualizaciones/geo/comunas_caba.geojson` (Buenos Aires Data;
  fuente y validación en `../6_visualizaciones/geo/FUENTE_GEOJSON.md`)

## Contenido

**KPIs:** precio promedio actual · variación interanual · ratio alquiler/sueldo ·
% de comunas por encima del umbral del 30 %.

**Filtros:** cantidad de ambientes (default 1) · rango de años (default últimos 3) · comuna.

**Gráficos y justificación de cada uno:**

| Gráfico | Pregunta | Por qué ese tipo |
|---|---|---|
| Línea — evolución de precios | 1 | Líneas: evolución temporal continua trimestre a trimestre |
| Línea — accesibilidad + umbral 30 % | 3 | Líneas con referencia: evolución de un indicador frente a un umbral |
| Dispersión — oferta vs. precio | 2 | Dispersión: relación entre dos variables numéricas (tamaño = superficie) |
| Mapa de símbolos — comunas | 2 | Distribución geográfica de oferta (tamaño) y precio (color) |

> Nota: el scatter y el mapa muestran todas las comunas del último período del rango; el
> selector de comuna afecta los KPIs y las series temporales. La «oferta estimada» es una
> variable derivada (superficie total ÷ superficie promedio de la ciudad). La Comuna 8 puede
> no aparecer en el mapa por falta de precio publicado (98 % de faltantes, ver perfilado).
