import {
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts"
import type { PuntoComuna } from "@/lib/metrics"
import { COLORS } from "@/lib/colors"

const fmtY = (v: number) =>
  v >= 1_000_000 ? `$${(v / 1_000_000).toFixed(1)}M` : `$${Math.round(v / 1000)}k`

export function OfferPriceScatter({ data, animMs }: { data: PuntoComuna[]; animMs: number }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <ScatterChart margin={{ top: 8, right: 16, bottom: 16, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
        <XAxis
          type="number"
          dataKey="cantidad"
          name="Oferta"
          tick={{ fontSize: 11 }}
          label={{ value: "Cantidad estimada de deptos", position: "insideBottom", offset: -8, fontSize: 11 }}
        />
        <YAxis
          type="number"
          dataKey="precio"
          name="Precio"
          tickFormatter={fmtY}
          tick={{ fontSize: 11 }}
          width={52}
        />
        <ZAxis type="number" dataKey="superficie" range={[60, 900]} name="Superficie" />
        <Tooltip
          cursor={{ strokeDasharray: "3 3" }}
          formatter={(v: unknown, n: unknown) => {
            const num = Number(v)
            if (n === "Precio") return ["$" + Math.round(num).toLocaleString("es-AR"), "Precio"]
            if (n === "Superficie") return [Math.round(num).toLocaleString("es-AR") + " m²", "Superficie"]
            return [Math.round(num), String(n)]
          }}
          labelFormatter={() => ""}
        />
        <Scatter
          data={data}
          fill={COLORS.azul}
          fillOpacity={0.6}
          stroke="#fff"
          animationDuration={animMs}
          isAnimationActive={animMs > 0}
        >
          <LabelList dataKey="comuna" position="center" formatter={(v) => `C${v}`} style={{ fontSize: 9, fill: "#16324a" }} />
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  )
}
