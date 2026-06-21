import { useState } from "react"
import { ChevronsUpDown, X } from "lucide-react"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface Props {
  value: number[]
  onChange: (v: number[]) => void
  options: number[]
}

export function MultiSelectComunas({ value, onChange, options }: Props) {
  const [open, setOpen] = useState(false)
  const disponibles = options.filter((o) => !value.includes(o))

  const agregar = (c: number) => onChange([...value, c].sort((a, b) => a - b))
  const quitar = (c: number) => onChange(value.filter((x) => x !== c))

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className="h-auto min-h-9 w-full justify-between gap-1 px-2 py-1"
        >
          <span className="flex flex-1 flex-wrap items-center gap-1">
            {value.length === 0 ? (
              <span className="px-1 text-muted-foreground">Todas las comunas</span>
            ) : (
              value.map((c) => (
                <Badge key={c} variant="secondary" className="gap-1 px-2 py-0.5 font-normal">
                  Comuna {c}
                  <span
                    role="button"
                    tabIndex={-1}
                    aria-label={`Quitar comuna ${c}`}
                    className="rounded-sm hover:bg-muted-foreground/20"
                    onClick={(e) => {
                      e.stopPropagation()
                      quitar(c)
                    }}
                  >
                    <X className="h-3 w-3" />
                  </span>
                </Badge>
              ))
            )}
          </span>
          <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[260px] p-0" align="start">
        <Command>
          <CommandInput placeholder="Buscar comuna..." />
          <CommandList>
            <CommandEmpty>Sin resultados.</CommandEmpty>
            <CommandGroup>
              {disponibles.map((c) => (
                <CommandItem
                  key={c}
                  value={`Comuna ${c}`}
                  onSelect={() => agregar(c)}
                >
                  Comuna {c}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
