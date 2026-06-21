import { useEffect, useMemo, useState } from "react"
import {
  aniosDisponibles,
  loadGeo,
  loadMaestro,
  type ComunasGeoJSON,
  type Filtros as TFiltros,
  type MaestroRow,
} from "@/lib/data"
import {
  calcularKpis,
  puntosPorComuna,
  serieRatio,
  seriePrecio,
  type SerieMulti,
} from "@/lib/metrics"
import { Filtros } from "@/components/Filtros"
import { KpiCards } from "@/components/KpiCards"
import { ChartCard } from "@/components/ChartCard"
import { PriceLineChart } from "@/components/charts/PriceLineChart"
import { AffordabilityChart } from "@/components/charts/AffordabilityChart"
import { OfferPriceScatter } from "@/components/charts/OfferPriceScatter"
import { ComunaMap } from "@/components/charts/ComunaMap"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function App() {
  const [rows, setRows] = useState<MaestroRow[] | null>(null)
  const [geo, setGeo] = useState<ComunasGeoJSON | null>(null)
  const [filtros, setFiltros] = useState<TFiltros>({
    ambientes: [1],
    anioDesde: 2018,
    anioHasta: 2026,
    comunas: [],
  })
  const [animMs, setAnimMs] = useState(250)

  useEffect(() => {
    loadMaestro().then((r) => {
      setRows(r)
      const anios = aniosDisponibles(r)
      const min = anios[0]
      const max = anios[anios.length - 1]
      setFiltros((f) => ({ ...f, anioDesde: Math.max(min, max - 2), anioHasta: max }))
    })
    loadGeo().then(setGeo)
  }, [])

  const anios = useMemo(() => (rows ? aniosDisponibles(rows) : []), [rows])
  const vacia: SerieMulti = { data: [], ambientes: [], conMax: false }
  const sPrecio = useMemo(() => (rows ? seriePrecio(rows, filtros) : vacia), [rows, filtros])
  const sRatio = useMemo(() => (rows ? serieRatio(rows, filtros) : vacia), [rows, filtros])
  const porComuna = useMemo(
    () => (rows ? puntosPorComuna(rows, filtros) : { periodo: "", puntos: [] }),
    [rows, filtros],
  )
  const kpis = useMemo(
    () => (rows ? calcularKpis(rows, filtros) : null),
    [rows, filtros],
  )

  if (!rows || !kpis) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Cargando datos…
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-7xl px-5 py-8">
        {/* Encabezado */}
        <header className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight">
            Mercado de alquiler de departamentos — CABA (2018–2026)
          </h1>
          <p className="text-sm text-muted-foreground">
            Dashboard interactivo · Calidad y Visualización de Datos · Datos: IDECBA y SEC La Plata
          </p>
        </header>

        {/* Filtros */}
        <Card className="mb-6">
          <CardContent className="py-4">
            <Filtros
              filtros={filtros}
              setFiltros={setFiltros}
              anios={anios}
              animMs={animMs}
              setAnimMs={setAnimMs}
            />
          </CardContent>
        </Card>

        {/* KPIs */}
        <div className="mb-6">
          <KpiCards kpis={kpis} />
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChartCard
            titulo="Evolución del precio de publicación"
            pregunta="Pregunta 1"
            justificacion="el gráfico de líneas muestra la evolución temporal continua del precio trimestre a trimestre."
            fuente="IDECBA (base Argenprop)"
          >
            <PriceLineChart serie={sPrecio} animMs={animMs} />
          </ChartCard>

          <ChartCard
            titulo="Accesibilidad: alquiler como % del sueldo"
            pregunta="Pregunta 3"
            justificacion="líneas con una línea de referencia para ver la evolución del ratio frente al umbral de asequibilidad (30%)."
            fuente="IDECBA + escalas salariales SEC La Plata"
          >
            <AffordabilityChart serie={sRatio} animMs={animMs} />
          </ChartCard>

          <ChartCard
            titulo="Relación entre oferta y precio por comuna"
            pregunta="Pregunta 2"
            justificacion="dispersión: relaciona dos variables numéricas (oferta y precio); el tamaño de burbuja agrega la superficie."
            fuente={`IDECBA · ${porComuna.periodo || "—"} · todas las comunas`}
          >
            <OfferPriceScatter data={porComuna.puntos} animMs={animMs} />
          </ChartCard>

          <ChartCard
            titulo="Oferta y precio en el mapa de comunas"
            pregunta="Pregunta 2"
            justificacion="mapa de símbolos: ubica geográficamente qué comunas concentran la oferta (tamaño) y a qué precio (color)."
            fuente="IDECBA + geometría de Buenos Aires Data"
          >
            <ComunaMap geo={geo} puntos={porComuna.puntos} />
          </ChartCard>
        </div>

        {/* Storytelling */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-base">La historia detrás de los datos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>
              <span className="font-semibold text-foreground">
                En CABA, alquilar dejó de ser accesible.
              </span>{" "}
              El alquiler de un monoambiente nunca representó menos de un tercio del sueldo
              básico de un empleado de comercio y, en 2023, llegó a superar un sueldo entero
              (108% en la Comuna 14).
            </p>
            <p>
              Aunque los precios nominales se multiplicaron unas 70 veces por la inflación, el
              dato decisivo es que crecieron por encima de las paritarias: incluso tras la
              recuperación posterior a 2023, el ratio nunca volvió a bajar del umbral del 30%.
            </p>
          </CardContent>
        </Card>

        <footer className="mt-8 text-center text-xs text-muted-foreground">
          Nota: los filtros (ambientes, años y comunas) afectan a todo el tablero. Con varias
          cantidades de ambientes, cada gráfico muestra una línea por tipología. La «oferta
          estimada» es una variable derivada (superficie total ÷ superficie promedio de la ciudad).
        </footer>
      </div>
    </div>
  )
}
