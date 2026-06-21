# 6. Dashboard
El dashboard es una app web implementada en React + shadcn/ui + Tailwind, que muestra la evolución del alquiler de departamentos en CABA (2018–2026) y responde a las tres preguntas de análisis. Arriba presenta cuatro KPIs (precio promedio, variación interanual, ratio alquiler/sueldo y % de comunas sobre el umbral del 30%) y una barra de filtros que afecta a todo el tablero en tiempo real: cantidad de ambientes (múltiple), rango de años, velocidad de transición y un selector múltiple de comunas con búsqueda. Debajo hay cuatro gráficos, cada uno justificado: líneas de evolución del precio, líneas del ratio alquiler/sueldo con referencia en el 30%, un scatter de oferta vs. precio por comuna y un mapa interactivo de comunas con burbujas (tamaño = oferta, color = precio). Todo se calcula en runtime sobre el dataset maestro sin modificarlo, con paleta apta para daltónicos, y cuenta una historia clara: alquilar en CABA dejó de ser accesible.

## Herramientas (stack)
Web app implementada en Vite + React + TypeScript + Tailwind + shadcn/ui, Recharts para los gráficos y d3-geo para el mapa.

## KPIs
- **Precio promedio**: mediana de comunas en el último trimestre del rango.
- **Variación interanual**: % de cambio del precio vs. el mismo trimestre del año anterior.
- **Alquiler / sueldo**:  % del sueldo básico que representa el alquiler (ratio de accesibilidad).
- **Comunas sobre 30%**: % de comunas por encima del umbral de asequibilidad.

## Screenshot completa

![Captura completa del dashboard](dashboard-fullpage-screenshot.png)

## Demo 
[Ver demo](https://dashboard-cvd-unsada.vercel.app/)

## Código fuente
[Ver código](https://github.com/EmilioGiordano/Dashboard-CVD-UNSAdA)
