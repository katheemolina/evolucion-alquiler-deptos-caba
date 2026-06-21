import type { ReactNode } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Props {
  titulo: string
  pregunta: string
  justificacion: string
  children: ReactNode
  fuente?: string
}

export function ChartCard({ titulo, pregunta, justificacion, children, fuente }: Props) {
  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-3">
          <CardTitle className="text-base leading-snug">{titulo}</CardTitle>
          <Badge variant="secondary" className="shrink-0 whitespace-nowrap">
            {pregunta}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground">
          <span className="font-medium text-foreground/70">Por qué este gráfico: </span>
          {justificacion}
        </p>
      </CardHeader>
      <CardContent>
        {children}
        {fuente && (
          <p className="mt-2 text-[11px] text-muted-foreground">Fuente: {fuente}</p>
        )}
      </CardContent>
    </Card>
  )
}
