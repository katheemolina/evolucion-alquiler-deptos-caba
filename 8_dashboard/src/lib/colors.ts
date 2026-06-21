// Paleta apta para daltónicos (Okabe-Ito), coherente con los gráficos del punto 6.
export const COLORS = {
  azul: "#0072B2",
  naranja: "#D55E00",
  rojo: "#CC3311",
  gris: "#BdBdBd",
  grisOscuro: "#555555",
}

// Color por cantidad de ambientes (para las series multi-línea).
export const AMB_COLOR: Record<number, string> = {
  1: "#0072B2", // azul
  2: "#D55E00", // naranja
  3: "#009E73", // verde
}

// Escala secuencial tipo viridis (5 stops) para el mapa.
const VIRIDIS = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"]

function hexToRgb(h: string) {
  const n = parseInt(h.slice(1), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

export function viridis(t: number): string {
  const x = Math.max(0, Math.min(1, t)) * (VIRIDIS.length - 1)
  const i = Math.floor(x)
  const f = x - i
  if (i >= VIRIDIS.length - 1) return VIRIDIS[VIRIDIS.length - 1]
  const a = hexToRgb(VIRIDIS[i])
  const b = hexToRgb(VIRIDIS[i + 1])
  const c = a.map((v, k) => Math.round(v + (b[k] - v) * f))
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`
}
