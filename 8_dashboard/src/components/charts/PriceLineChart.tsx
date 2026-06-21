import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { SerieMulti } from "@/lib/metrics"
import { AMB_COLOR } from "@/lib/colors"

const fmtY = (v: number) =>
  v >= 1_000_000 ? `$${(v / 1_000_000).toFixed(1)}M` : `$${Math.round(v / 1000)}k`

export function PriceLineChart({ serie, animMs }: { serie: SerieMulti; animMs: number }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={serie.data} margin={{ top: 8, right: 16, bottom: 4, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
        <XAxis dataKey="periodo" tick={{ fontSize: 11 }} interval="preserveStartEnd" minTickGap={24} />
        <YAxis tickFormatter={fmtY} tick={{ fontSize: 11 }} width={52} />
        <Tooltip
          formatter={(v: unknown, n: unknown) => [
            "$" + Math.round(Number(v)).toLocaleString("es-AR"),
            `${String(n).replace("a", "")} amb.`,
          ]}
          labelStyle={{ fontWeight: 600 }}
        />
        {serie.ambientes.length > 1 && (
          <Legend wrapperStyle={{ fontSize: 11 }} formatter={(n) => `${String(n).replace("a", "")} amb.`} />
        )}
        {serie.ambientes.map((amb) => (
          <Line
            key={amb}
            type="monotone"
            dataKey={`a${amb}`}
            name={`a${amb}`}
            stroke={AMB_COLOR[amb]}
            strokeWidth={2.5}
            dot={false}
            connectNulls
            animationDuration={animMs}
            isAnimationActive={animMs > 0}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
