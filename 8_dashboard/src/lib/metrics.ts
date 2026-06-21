// Cálculos derivados de los datos según los filtros activos.
// Todo se computa en runtime; no se altera el dataset.

import type { Filtros, MaestroRow } from "./data"

export const UMBRAL = 30 // % de asequibilidad
export const AMBIENTES = [1, 2, 3]

export function mediana(nums: number[]): number | null {
  const xs = nums.filter((n) => Number.isFinite(n)).sort((a, b) => a - b)
  if (xs.length === 0) return null
  const mid = Math.floor(xs.length / 2)
  return xs.length % 2 ? xs[mid] : (xs[mid - 1] + xs[mid]) / 2
}

const suma = (nums: number[]) => nums.reduce((a, b) => a + b, 0)

// Aplica el alcance del filtro: ambientes seleccionados, rango de años y comunas.
function scoped(rows: MaestroRow[], f: Filtros): MaestroRow[] {
  return rows.filter(
    (r) =>
      f.ambientes.includes(r.ambientes) &&
      r.anio >= f.anioDesde &&
      r.anio <= f.anioHasta &&
      (f.comunas.length === 0 || f.comunas.includes(r.comuna)),
  )
}

export interface SerieRow {
  periodo: string
  order: number
  [key: string]: number | string | null
}

export interface SerieMulti {
  data: SerieRow[]
  ambientes: number[]
  conMax: boolean
}

// Serie temporal multi-ambiente: una clave `a{amb}` por cada cantidad de ambientes,
// con la mediana de las comunas dentro del alcance en cada período.
function serieMulti(
  rows: MaestroRow[],
  f: Filtros,
  campo: "precio" | "ratioPct",
): SerieMulti {
  const base = scoped(rows, f)
  const ambs = [...f.ambientes].sort((a, b) => a - b)
  const conMax = ambs.length === 1 // línea del "peor caso" sólo con un ambiente

  const porOrden = new Map<number, MaestroRow[]>()
  for (const r of base) {
    if (!porOrden.has(r.order)) porOrden.set(r.order, [])
    porOrden.get(r.order)!.push(r)
  }

  const data: SerieRow[] = []
  for (const [order, grupo] of porOrden) {
    const row: SerieRow = { periodo: grupo[0].periodo, order }
    for (const amb of ambs) {
      const vals = grupo
        .filter((r) => r.ambientes === amb)
        .map((r) => r[campo])
        .filter((v): v is number => v != null)
      row[`a${amb}`] = vals.length ? mediana(vals) : null
    }
    if (conMax) {
      const todos = grupo.map((r) => r[campo]).filter((v): v is number => v != null)
      row.max = todos.length ? Math.max(...todos) : null
    }
    data.push(row)
  }
  data.sort((a, b) => a.order - b.order)
  return { data, ambientes: ambs, conMax }
}

export const seriePrecio = (rows: MaestroRow[], f: Filtros) => serieMulti(rows, f, "precio")
export const serieRatio = (rows: MaestroRow[], f: Filtros) => serieMulti(rows, f, "ratioPct")

export interface PuntoComuna {
  comuna: number
  cantidad: number
  precio: number
  superficie: number
  ratioPct: number | null
}

// Último período con datos dentro del alcance (para scatter y mapa).
export function ultimoPeriodo(rows: MaestroRow[], f: Filtros): number | null {
  const base = scoped(rows, f).filter((r) => r.precio != null)
  if (!base.length) return null
  return Math.max(...base.map((r) => r.order))
}

// Una fila por comuna, agregando las cantidades de ambientes seleccionadas.
export function puntosPorComuna(rows: MaestroRow[], f: Filtros): {
  periodo: string
  puntos: PuntoComuna[]
} {
  const order = ultimoPeriodo(rows, f)
  if (order == null) return { periodo: "", puntos: [] }
  const base = scoped(rows, f).filter((r) => r.order === order)

  const porComuna = new Map<number, MaestroRow[]>()
  for (const r of base) {
    if (!porComuna.has(r.comuna)) porComuna.set(r.comuna, [])
    porComuna.get(r.comuna)!.push(r)
  }

  const puntos: PuntoComuna[] = []
  for (const [comuna, grupo] of porComuna) {
    const precios = grupo.map((r) => r.precio).filter((v): v is number => v != null)
    const cants = grupo.map((r) => r.cantidad).filter((v): v is number => v != null)
    const sups = grupo.map((r) => r.superficie).filter((v): v is number => v != null)
    const ratios = grupo.map((r) => r.ratioPct).filter((v): v is number => v != null)
    if (!precios.length || !cants.length) continue
    puntos.push({
      comuna,
      precio: mediana(precios)!,
      cantidad: suma(cants),
      superficie: suma(sups),
      ratioPct: ratios.length ? mediana(ratios) : null,
    })
  }
  const periodo = base[0]?.periodo ?? ""
  return { periodo, puntos: puntos.sort((a, b) => a.comuna - b.comuna) }
}

export interface Kpis {
  periodo: string
  precioMediana: number | null
  variacionInteranual: number | null
  ratioMediana: number | null
  pctSobreUmbral: number | null
}

export function calcularKpis(rows: MaestroRow[], f: Filtros): Kpis {
  const order = ultimoPeriodo(rows, f)
  if (order == null) {
    return {
      periodo: "",
      precioMediana: null,
      variacionInteranual: null,
      ratioMediana: null,
      pctSobreUmbral: null,
    }
  }
  const enOrden = (o: number) => scoped(rows, f).filter((r) => r.order === o)
  const actual = enOrden(order)
  const precioMediana = mediana(
    actual.map((r) => r.precio).filter((v): v is number => v != null),
  )
  const ratioMediana = mediana(
    actual.map((r) => r.ratioPct).filter((v): v is number => v != null),
  )
  const precioPrevio = mediana(
    enOrden(order - 4)
      .map((r) => r.precio)
      .filter((v): v is number => v != null),
  )
  const variacionInteranual =
    precioMediana != null && precioPrevio != null && precioPrevio > 0
      ? ((precioMediana - precioPrevio) / precioPrevio) * 100
      : null

  const ratios = actual.map((r) => r.ratioPct).filter((v): v is number => v != null)
  const pctSobreUmbral = ratios.length
    ? (ratios.filter((v) => v > UMBRAL).length / ratios.length) * 100
    : null

  return {
    periodo: actual[0]?.periodo ?? "",
    precioMediana,
    variacionInteranual,
    ratioMediana,
    pctSobreUmbral,
  }
}

// Formateadores
export const fmtPesos = (v: number | null) =>
  v == null ? "—" : "$" + Math.round(v).toLocaleString("es-AR")
export const fmtPct = (v: number | null, dec = 0) =>
  v == null ? "—" : v.toFixed(dec) + "%"
