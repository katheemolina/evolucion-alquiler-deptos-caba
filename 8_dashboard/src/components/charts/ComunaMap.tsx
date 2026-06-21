import { useEffect, useMemo, useRef, useState } from "react"
import type { MouseEvent as RMouseEvent, PointerEvent as RPointerEvent } from "react"
import { geoMercator, geoPath } from "d3-geo"
import type { ComunasGeoJSON } from "@/lib/data"
import type { PuntoComuna } from "@/lib/metrics"
import { viridis } from "@/lib/colors"
import { Button } from "@/components/ui/button"

const W = 520
const H = 560
const HL = "#0072B2"

// Limita zoom (1×–8×) y desplazamiento para que el mapa nunca se salga de la vista.
function clampT(k: number, x: number, y: number) {
  const kk = Math.min(8, Math.max(1, k))
  const minX = W * (1 - kk)
  const minY = H * (1 - kk)
  return {
    k: kk,
    x: Math.min(0, Math.max(minX, x)),
    y: Math.min(0, Math.max(minY, y)),
  }
}

interface Feat {
  comuna: number
  barrios: string
  d: string
  cx: number
  cy: number
  punto?: PuntoComuna
}

export function ComunaMap({
  geo,
  puntos,
}: {
  geo: ComunasGeoJSON | null
  puntos: PuntoComuna[]
}) {
  const contRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const [t, setT] = useState({ k: 1, x: 0, y: 0 })
  const [hover, setHover] = useState<{ comuna: number; x: number; y: number } | null>(null)
  const drag = useRef<{ x: number; y: number; ox: number; oy: number } | null>(null)

  const datos = useMemo(() => {
    if (!geo) return null
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const projection = geoMercator().fitSize([W, H], geo as any)
    const path = geoPath(projection)
    const porComuna = new Map(puntos.map((p) => [p.comuna, p]))
    const precios = puntos.map((p) => p.precio)
    const cantidades = puntos.map((p) => p.cantidad)
    const minP = precios.length ? Math.min(...precios) : 0
    const maxP = precios.length ? Math.max(...precios) : 1
    const maxC = cantidades.length ? Math.max(...cantidades) : 1
    const feats: Feat[] = geo.features.map((f) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const ff = f as any
      return {
        comuna: f.properties.comuna,
        barrios: String(f.properties.barrios ?? ""),
        d: path(ff) ?? "",
        cx: path.centroid(ff)[0],
        cy: path.centroid(ff)[1],
        punto: porComuna.get(f.properties.comuna),
      }
    })
    return { feats, minP, maxP, maxC }
  }, [geo, puntos])

  // Zoom con la rueda (listener no pasivo para poder preventDefault)
  useEffect(() => {
    const svg = svgRef.current
    if (!svg) return
    const onWheel = (e: WheelEvent) => {
      e.preventDefault()
      const r = svg.getBoundingClientRect()
      const sx = ((e.clientX - r.left) / r.width) * W
      const sy = ((e.clientY - r.top) / r.height) * H
      setT((p) => {
        const f = Math.exp(-e.deltaY * 0.0015)
        const k = Math.min(8, Math.max(1, p.k * f))
        const ux = (sx - p.x) / p.k
        const uy = (sy - p.y) / p.k
        return clampT(k, sx - ux * k, sy - uy * k)
      })
    }
    svg.addEventListener("wheel", onWheel, { passive: false })
    return () => svg.removeEventListener("wheel", onWheel)
  }, [])

  if (!datos) return <div className="h-[420px]" />
  const { feats, minP, maxP, maxC } = datos
  const rDe = (c: number) => 5 + Math.sqrt(c / maxC) * 19
  const hoverFeat = hover ? feats.find((f) => f.comuna === hover.comuna) : null

  const posRelativa = (clientX: number, clientY: number) => {
    const r = contRef.current!.getBoundingClientRect()
    return { x: clientX - r.left, y: clientY - r.top }
  }

  const onDown = (e: RPointerEvent<SVGSVGElement>) => {
    drag.current = { x: e.clientX, y: e.clientY, ox: t.x, oy: t.y }
    try {
      e.currentTarget.setPointerCapture(e.pointerId)
    } catch {
      /* pointerId no capturable (p. ej. en tests) */
    }
  }
  const onMove = (e: RPointerEvent<SVGSVGElement>) => {
    const d = drag.current
    if (!d) return
    const r = svgRef.current!.getBoundingClientRect()
    const dx = ((e.clientX - d.x) / r.width) * W
    const dy = ((e.clientY - d.y) / r.height) * H
    setT((p) => clampT(p.k, d.ox + dx, d.oy + dy))
  }
  const onUp = () => {
    drag.current = null
  }

  // Zoom con botones, centrado en el medio del mapa
  const zoomBy = (f: number) =>
    setT((p) => {
      const k = Math.min(8, Math.max(1, p.k * f))
      const cx = W / 2
      const cy = H / 2
      const ux = (cx - p.x) / p.k
      const uy = (cy - p.y) / p.k
      return clampT(k, cx - ux * k, cy - uy * k)
    })

  const enterFeat = (f: Feat) => (e: RMouseEvent) =>
    setHover({ comuna: f.comuna, ...posRelativa(e.clientX, e.clientY) })

  return (
    <div ref={contRef} className="relative">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${W} ${H}`}
        className="h-[420px] w-full cursor-grab touch-none rounded-md bg-slate-50 active:cursor-grabbing"
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerLeave={() => {
          onUp()
          setHover(null)
        }}
      >
        <g transform={`translate(${t.x},${t.y}) scale(${t.k})`}>
          {feats.map((f) => {
            const activo = hover?.comuna === f.comuna
            return (
              <path
                key={`p-${f.comuna}`}
                d={f.d}
                fill={activo ? "#cfe3f3" : "#ededed"}
                stroke={activo ? HL : "#ffffff"}
                strokeWidth={(activo ? 2 : 1.2) / t.k}
                onMouseEnter={enterFeat(f)}
                onMouseMove={enterFeat(f)}
              />
            )
          })}
          {feats.map((f) =>
            f.punto ? (
              <g key={`b-${f.comuna}`} pointerEvents="none">
                <circle
                  cx={f.cx}
                  cy={f.cy}
                  r={rDe(f.punto.cantidad)}
                  fill={viridis((f.punto.precio - minP) / (maxP - minP || 1))}
                  fillOpacity={0.85}
                  stroke="#fff"
                  strokeWidth={1.5 / t.k}
                />
                <text
                  x={f.cx}
                  y={f.cy}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize={9}
                  fontWeight={700}
                  fill="#fff"
                >
                  {f.comuna}
                </text>
              </g>
            ) : null,
          )}
        </g>
      </svg>

      {/* Tooltip */}
      {hoverFeat && hover && (
        <div
          className="pointer-events-none absolute z-10 max-w-[220px] rounded-md border bg-white/95 p-2 text-xs shadow-md"
          style={{
            left: Math.min(hover.x + 12, 320),
            top: hover.y + 12,
          }}
        >
          <p className="font-semibold text-foreground">Comuna {hoverFeat.comuna}</p>
          <p className="text-muted-foreground">{hoverFeat.barrios}</p>
          {hoverFeat.punto ? (
            <p className="mt-1 text-foreground">
              ${Math.round(hoverFeat.punto.precio).toLocaleString("es-AR")} ·{" "}
              {Math.round(hoverFeat.punto.cantidad)} deptos
            </p>
          ) : (
            <p className="mt-1 italic text-muted-foreground">Sin dato de precio en el período</p>
          )}
        </div>
      )}

      {/* Controles de zoom */}
      <div className="absolute right-2 top-2 flex items-center gap-1">
        {(t.k !== 1 || t.x !== 0 || t.y !== 0) && (
          <Button
            variant="secondary"
            size="sm"
            className="h-8 text-xs"
            onClick={() => setT({ k: 1, x: 0, y: 0 })}
          >
            Reiniciar
          </Button>
        )}
        <Button
          variant="secondary"
          size="icon"
          className="h-8 w-8 text-lg leading-none"
          onClick={() => zoomBy(1 / 1.4)}
          aria-label="Alejar"
        >
          −
        </Button>
        <Button
          variant="secondary"
          size="icon"
          className="h-8 w-8 text-lg leading-none"
          onClick={() => zoomBy(1.4)}
          aria-label="Acercar"
        >
          +
        </Button>
      </div>

      {/* Leyenda + ayuda */}
      <div className="mt-3 flex items-center gap-3 text-[11px] text-muted-foreground">
        <span>{`$${Math.round(minP / 1000)}k`}</span>
        <div
          className="h-2 flex-1 rounded"
          style={{ background: "linear-gradient(90deg,#440154,#3b528b,#21918c,#5ec962,#fde725)" }}
        />
        <span>{`$${Math.round(maxP / 1000)}k`}</span>
        <span className="ml-2">Tamaño = oferta</span>
      </div>
      <p className="mt-1 text-[11px] text-muted-foreground">
        Botones + / − o rueda para zoom · arrastrar para mover · pasar el mouse para ver cada comuna
      </p>
    </div>
  )
}
