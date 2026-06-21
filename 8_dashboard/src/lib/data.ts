// Carga y parseo del dataset maestro (sin modificar el archivo fuente).
// La fecha se deriva en runtime a partir de `periodo_trim` ("2018-Q1").

export interface MaestroRow {
  comuna: number
  periodo: string
  ambientes: number
  precio: number | null
  provisorio: boolean | null
  sueldo: number | null
  ratioPct: number | null
  mesesSueldo: number | null
  superficie: number | null
  cantidad: number | null
  anio: number
  trimestre: number
  order: number
}

export interface Filtros {
  ambientes: number[] // cantidades de ambientes a mostrar (1+); cada una = una línea
  anioDesde: number
  anioHasta: number
  comunas: number[] // alcance: comunas a incluir; vacío = todas
}

function num(v: string | undefined): number | null {
  if (v === undefined || v.trim() === "") return null
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

export function parsePeriodo(p: string): { anio: number; trimestre: number; order: number } {
  const [a, q] = p.split("-Q")
  const anio = parseInt(a, 10)
  const trimestre = parseInt(q, 10)
  return { anio, trimestre, order: anio * 4 + trimestre }
}

const BASE = import.meta.env.BASE_URL

export async function loadMaestro(): Promise<MaestroRow[]> {
  const res = await fetch(`${BASE}data/dataset_maestro.csv`)
  const text = await res.text()
  const lines = text.trim().split(/\r?\n/)
  const header = lines[0].split(",")
  const idx = (name: string) => header.indexOf(name)
  const iC = idx("comuna")
  const iP = idx("periodo_trim")
  const iA = idx("ambientes")
  const iPr = idx("precio_promedio_pesos")
  const iProv = idx("provisorio")
  const iS = idx("sueldo_basico_admin_a")
  const iR = idx("ratio_alquiler_sueldo_pct")
  const iM = idx("meses_sueldo_para_alquiler")
  const iSup = idx("superficie_total_m2")
  const iCant = idx("cantidad_deptos_estimada")

  const rows: MaestroRow[] = []
  for (let k = 1; k < lines.length; k++) {
    const c = lines[k].split(",")
    const periodo = c[iP]
    const { anio, trimestre, order } = parsePeriodo(periodo)
    const prov = c[iProv]?.trim()
    rows.push({
      comuna: Number(c[iC]),
      periodo,
      ambientes: Number(c[iA]),
      precio: num(c[iPr]),
      provisorio: prov === "" || prov === undefined ? null : prov === "True",
      sueldo: num(c[iS]),
      ratioPct: num(c[iR]),
      mesesSueldo: num(c[iM]),
      superficie: num(c[iSup]),
      cantidad: num(c[iCant]),
      anio,
      trimestre,
      order,
    })
  }
  return rows
}

// GeoJSON de comunas (tipado laxo: solo necesitamos geometry + properties.comuna)
export type ComunasGeoJSON = {
  type: string
  features: Array<{
    type: string
    properties: { comuna: number; [k: string]: unknown }
    geometry: { type: string; coordinates: unknown }
  }>
}

export async function loadGeo(): Promise<ComunasGeoJSON> {
  const res = await fetch(`${BASE}data/comunas_caba.geojson`)
  return res.json()
}

export function aniosDisponibles(rows: MaestroRow[]): number[] {
  return Array.from(new Set(rows.map((r) => r.anio))).sort((a, b) => a - b)
}
