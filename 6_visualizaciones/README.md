# Punto 6 — Diseño de visualizaciones iniciales

Visualizaciones del TFI (Mercado de alquiler de departamentos en CABA, 2018–2026).
Las 4 imágenes responden a las 3 preguntas de análisis del punto 5. Se generan de
forma reproducible con `generar_graficos_evidencia.py` (lee `../dataset_maestro.csv`).

Marco aplicado: *Datos que cuentan historias* (Knaflic / GICS-UNNE): título de acción,
decluttering, color para enfocar la atención, paleta apta para daltónicos (Okabe-Ito)
y etiquetado directo.

## Mapa pregunta → gráfico

| Gráfico | Archivo | Pregunta | Tipo de gráfico |
|---|---|---|---|
| 1 | `grafico_1_precios.png` | Pregunta 1 | Líneas (evolución temporal) |
| 2 | `grafico_2_oferta_precio.png` | Pregunta 2 (relación) | Dispersión / burbujas |
| 3 | `grafico_3_mapa_burbujas.png` | Pregunta 2 (geográfico) | Mapa de símbolos |
| 4 | `grafico_4_accesibilidad.png` | Pregunta 3 | Líneas + línea de referencia |

> La Pregunta 2 se aborda con dos visualizaciones complementarias: el Gráfico 2
> cuantifica la relación oferta–precio (r = 0.73) y el Gráfico 3 muestra su
> distribución geográfica por comuna.

---

## Gráfico 1 — Evolución de precios (Pregunta 1)

**Responde a:** ¿Cómo evolucionó el precio promedio de publicación de alquiler entre
2018 y 2026 según comuna y cantidad de ambientes?

**Justificación del tipo de gráfico:** se eligió un gráfico de **líneas** porque la
pregunta indaga la **evolución temporal** del precio; el facetado por cantidad de
ambientes permite comparar las tres tipologías sin superponer series, y la **escala
logarítmica** evita que el crecimiento por inflación aplaste la lectura de los
primeros años.

**Hallazgo:** el precio nominal se multiplicó por ~70 veces en todas las comunas
(crecimiento dominado por la inflación del período).

---

## Gráfico 2 — Relación oferta vs. precio (Pregunta 2, parte "relación")

**Responde a:** la parte de la Pregunta 2 sobre *cómo se relaciona el volumen estimado
de departamentos con el nivel de precios*, cuantificándola con el coeficiente de
correlación (r = 0.73).

**Justificación del tipo de gráfico:** se eligió un gráfico de **dispersión (burbujas)**
porque la pregunta busca la **relación entre dos variables numéricas** (oferta y precio);
el tamaño de burbuja incorpora una tercera variable (superficie) y la línea de tendencia
con el coeficiente r cuantifica la relación.

**Hallazgo:** las comunas con más oferta tienden a ser las más caras (relación positiva
moderada, r = 0.73): más oferta no abarata.

---

## Gráfico 3 — Mapa de oferta y precio por comuna (Pregunta 2, parte "geográfica")

**Responde a:** la parte de la Pregunta 2 sobre *qué comunas concentran mayor
superficie/oferta en alquiler*, mostrando la distribución geográfica de la oferta y el
precio.

**Justificación del tipo de gráfico:** se eligió un **mapa de símbolos (bubble map)**
porque la pregunta tiene un componente **geográfico**; el tamaño de burbuja representa la
oferta estimada y el color, el precio promedio, ubicados sobre el mapa real de las comunas.

**Hallazgo:** las comunas del norte (13, 14, 2) concentran la mayor oferta y los precios
más altos.

**Insumo cartográfico:** GeoJSON oficial de comunas de Buenos Aires Data (ver
`geo/FUENTE_GEOJSON.md`). La asignación comuna↔geometría fue validada contra la tabla de
equivalencia barrio↔comuna del proyecto (dataset 1.4). La Comuna 8 no aparece porque no
tiene precio publicado en el período (98 % de faltantes; documentado en el perfilado).

---

## Gráfico 4 — Accesibilidad alquiler/sueldo (Pregunta 3)

**Responde a:** ¿Qué proporción del sueldo básico representa el alquiler según comuna y
trimestre, y qué comunas superan el umbral de referencia del 30 %?

**Justificación del tipo de gráfico:** se eligió un gráfico de **líneas con línea de
referencia** porque la pregunta analiza la **evolución de un indicador frente a un umbral**
(30 % de asequibilidad); la mediana resume la tendencia central y la zona sombreada
refuerza que el ratio se mantuvo siempre por encima del umbral.

**Hallazgo:** el alquiler de un monoambiente nunca bajó del 30 % del sueldo y en 2023
llegó a superar un sueldo entero (108 % en la Comuna 14).

---

## Reproducir

```bash
cd 6_visualizaciones
python generar_graficos_evidencia.py
```

Requisitos: `pandas`, `numpy`, `matplotlib`, `seaborn`.
Entrada: `../dataset_maestro.csv` y `geo/comunas_caba.geojson`.
Salida: los 4 `grafico_*.png` (300 dpi) en esta carpeta.
