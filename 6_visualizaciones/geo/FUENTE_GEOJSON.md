# Fuente del archivo cartográfico (mapa de comunas)

**Archivo:** `comunas_caba.geojson` (15 comunas, MultiPolygon, ~584 KB)

**Fuente:** Buenos Aires Data — Gobierno de la Ciudad de Buenos Aires (GCBA), dataset "Comunas".

**URL de descarga:**
https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ministerio-de-educacion/comunas/comunas.geojson

**Portal del dataset:** https://data.buenosaires.gob.ar/dataset/comunas

**Fecha de obtención:** 20/06/2026

**Uso en el TFI:** insumo cartográfico para el mapa de símbolos (bubble map) del punto 6
(Gráfico 4 — distribución geográfica de oferta y precio por comuna).

**Campos:** `id`, `objeto`, `comuna` (1–15), `barrios`, `perimetro`, `area`.

**Validación realizada (20/06/2026):** se cruzó el campo `barrios` de cada comuna contra la
tabla de equivalencia barrio↔comuna del proyecto (dataset 1.4). Las 15 comunas coinciden;
las únicas diferencias son de formato/encoding del mismo barrio:
- Comuna 4: "La Boca" (geojson) = "Boca" (tabla).
- Comuna 13: "Núñez" (geojson) = "NUÃ'EZ"/"Nuaez" (artefacto de encoding ya documentado en el perfilado).

Conclusión: la asignación geográfica del mapa es correcta.
