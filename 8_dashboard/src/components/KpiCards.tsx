import { Card, CardContent } from "@/components/ui/card"
import type { Kpis } from "@/lib/metrics"
import { fmtPesos, fmtPct, UMBRAL } from "@/lib/metrics"

function KpiCard({
  titulo,
  valor,
  detalle,
  acento,
}: {
  titulo: string
  valor: string
  detalle: string
  acento?: "ok" | "alerta"
}) {
  const color =
    acento === "alerta"
      ? "text-red-600"
      : acento === "ok"
        ? "text-emerald-600"
        : "text-foreground"
  return (
    <Card className="shadow-sm">
      <CardContent className="px-5 py-1">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {titulo}
        </p>
        <p className={`mt-1 text-3xl font-semibold tabular-nums ${color}`}>{valor}</p>
        <p className="mt-1 text-xs text-muted-foreground">{detalle}</p>
      </CardContent>
    </Card>
  )
}

export function KpiCards({ kpis }: { kpis: Kpis }) {
  const periodo = kpis.periodo || "—"
  const variacion =
    kpis.variacionInteranual == null
      ? "—"
      : (kpis.variacionInteranual >= 0 ? "+" : "") +
        kpis.variacionInteranual.toFixed(0) +
        "%"

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <KpiCard
        titulo="Precio promedio"
        valor={fmtPesos(kpis.precioMediana)}
        detalle={`Mediana de comunas · ${periodo}`}
      />
      <KpiCard
        titulo="Variación interanual"
        valor={variacion}
        detalle="Precio vs. mismo trimestre del año anterior"
        acento={kpis.variacionInteranual != null && kpis.variacionInteranual > 0 ? "alerta" : undefined}
      />
      <KpiCard
        titulo="Alquiler / sueldo"
        valor={fmtPct(kpis.ratioMediana)}
        detalle={`% del sueldo básico · ${periodo}`}
        acento={kpis.ratioMediana != null && kpis.ratioMediana > UMBRAL ? "alerta" : "ok"}
      />
      <KpiCard
        titulo={`Comunas sobre ${UMBRAL}%`}
        valor={fmtPct(kpis.pctSobreUmbral)}
        detalle="Por encima del umbral de asequibilidad"
        acento={kpis.pctSobreUmbral != null && kpis.pctSobreUmbral >= 50 ? "alerta" : undefined}
      />
    </div>
  )
}
