import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { SerieMulti } from "@/lib/metrics"
import { UMBRAL } from "@/lib/metrics"
import { AMB_COLOR, COLORS } from "@/lib/colors"

export function AffordabilityChart({
  serie,
  animMs,
}: {
  serie: SerieMulti
  animMs: number
}) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={serie.data} margin={{ top: 8, right: 16, bottom: 4, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
        <XAxis dataKey="periodo" tick={{ fontSize: 11 }} interval="preserveStartEnd" minTickGap={24} />
        <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} width={40} domain={[0, "auto"]} />
        <ReferenceArea y1={UMBRAL} y2={9999} fill={COLORS.rojo} fillOpacity={0.06} />
        <ReferenceLine
          y={UMBRAL}
          stroke={COLORS.rojo}
          strokeDasharray="6 4"
          strokeWidth={2}
          label={{ value: `Umbral ${UMBRAL}%`, position: "insideBottomLeft", fill: COLORS.rojo, fontSize: 11 }}
        />
        <Tooltip
          formatter={(v: unknown, n: unknown) => {
            const k = String(n)
            const label = k === "max" ? "Comuna más cara" : `${k.replace("a", "")} amb.`
            return [`${Number(v).toFixed(0)}%`, label]
          }}
        />
        <Legend
          wrapperStyle={{ fontSize: 11 }}
          formatter={(n) => (String(n) === "max" ? "Comuna más cara" : `${String(n).replace("a", "")} amb.`)}
        />
        {serie.conMax && (
          <Line
            type="monotone"
            dataKey="max"
            name="max"
            stroke={COLORS.naranja}
            strokeWidth={1.4}
            dot={false}
            connectNulls
            animationDuration={animMs}
            isAnimationActive={animMs > 0}
          />
        )}
        {serie.ambientes.map((amb) => (
          <Line
            key={amb}
            type="monotone"
            dataKey={`a${amb}`}
            name={`a${amb}`}
            stroke={AMB_COLOR[amb]}
            strokeWidth={3}
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
