import type { Filtros as F } from "@/lib/data"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { Slider } from "@/components/ui/slider"
import { Button } from "@/components/ui/button"
import { MultiSelectComunas } from "@/components/MultiSelectComunas"

interface Props {
  filtros: F
  setFiltros: (f: F) => void
  anios: number[]
  animMs: number
  setAnimMs: (v: number) => void
}

export function Filtros({ filtros, setFiltros, anios, animMs, setAnimMs }: Props) {
  const minAnio = anios[0]
  const maxAnio = anios[anios.length - 1]

  const velocidad =
    animMs === 0 ? "Instantánea" : animMs <= 300 ? "Rápida" : animMs <= 700 ? "Media" : "Suave"

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-5 md:flex-row md:flex-wrap md:items-end md:gap-8">
        {/* Cantidad de ambientes (múltiple) */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-medium text-muted-foreground">
            Cantidad de ambientes
          </label>
          <ToggleGroup
            type="multiple"
            value={filtros.ambientes.map(String)}
            onValueChange={(v) =>
              v.length && setFiltros({ ...filtros, ambientes: v.map(Number).sort() })
            }
            variant="outline"
          >
            <ToggleGroupItem value="1" className="px-4">1 amb.</ToggleGroupItem>
            <ToggleGroupItem value="2" className="px-4">2 amb.</ToggleGroupItem>
            <ToggleGroupItem value="3" className="px-4">3 amb.</ToggleGroupItem>
          </ToggleGroup>
        </div>

        {/* Rango de años */}
        <div className="flex min-w-[220px] flex-col gap-2">
          <label className="text-xs font-medium text-muted-foreground">
            Rango de años:{" "}
            <span className="font-semibold text-foreground">
              {filtros.anioDesde}–{filtros.anioHasta}
            </span>
          </label>
          <Slider
            min={minAnio}
            max={maxAnio}
            step={1}
            value={[filtros.anioDesde, filtros.anioHasta]}
            onValueChange={([d, h]) => setFiltros({ ...filtros, anioDesde: d, anioHasta: h })}
            className="mt-2"
          />
        </div>

        {/* Velocidad de transición */}
        <div className="flex min-w-[200px] flex-col gap-2">
          <label className="text-xs font-medium text-muted-foreground">
            Velocidad de transición:{" "}
            <span className="font-semibold text-foreground">{velocidad}</span>
          </label>
          <Slider
            min={0}
            max={1000}
            step={100}
            value={[animMs]}
            onValueChange={([v]) => setAnimMs(v)}
            className="mt-2"
          />
        </div>
      </div>

        {/* Comunas (alcance, multi-select con búsqueda) */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <label className="text-xs font-medium text-muted-foreground">
              Comunas <span className="text-muted-foreground/70">(ninguna = todas)</span>
            </label>
            {filtros.comunas.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs"
                onClick={() => setFiltros({ ...filtros, comunas: [] })}
              >
                Limpiar
              </Button>
            )}
          </div>
          <MultiSelectComunas
            value={filtros.comunas}
            onChange={(c) => setFiltros({ ...filtros, comunas: c })}
            options={Array.from({ length: 15 }, (_, i) => i + 1)}
          />
        </div>
    </div>
  )
}
