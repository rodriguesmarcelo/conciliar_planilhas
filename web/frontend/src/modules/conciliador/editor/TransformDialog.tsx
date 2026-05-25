import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ALL_TRANSFORMS } from "./constants"

function buttonLabel(value: string[]): string {
  if (value.length === 0) return "Nenhuma"
  if (value.length === 1) {
    const found = ALL_TRANSFORMS.find(([key]) => key === value[0])
    return found ? found[1] : value[0]
  }
  return `${value.length} selecionadas`
}

export function TransformDialog({
  value,
  onChange,
}: {
  value: string[]
  onChange: (next: string[]) => void
}) {
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState<string[]>(value)

  function handleOpenChange(next: boolean) {
    if (next) setDraft(value)
    setOpen(next)
  }

  function toggle(key: string) {
    setDraft((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key],
    )
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger
        render={<Button variant="outline" size="sm" className="w-full justify-start truncate" />}
      >
        {buttonLabel(value)}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Transformações</DialogTitle>
        </DialogHeader>
        <div className="space-y-2">
          {ALL_TRANSFORMS.map(([key, label]) => (
            <div key={key} className="flex items-center gap-2">
              <Checkbox
                id={`tr-${key}`}
                checked={draft.includes(key)}
                onCheckedChange={() => toggle(key)}
              />
              <label htmlFor={`tr-${key}`} className="text-sm leading-none select-none">
                {label}
              </label>
            </div>
          ))}
        </div>
        <DialogFooter>
          <DialogClose render={<Button variant="outline" />}>Cancelar</DialogClose>
          <Button
            onClick={() => {
              onChange(draft)
              setOpen(false)
            }}
          >
            Confirmar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
