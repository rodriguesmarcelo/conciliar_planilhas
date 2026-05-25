import { Plus } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ColumnRow } from "./ColumnRow"
import { PreviewTable } from "./PreviewTable"
import {
  COL_GRID,
  newColumn,
  type EditorColumn,
  type EditorSheet,
} from "./constants"

export function SheetPanel({
  sheet,
  onChange,
}: {
  sheet: EditorSheet
  onChange: (next: EditorSheet) => void
}) {
  function update(patch: Partial<EditorSheet>) {
    onChange({ ...sheet, ...patch })
  }

  function addColumn() {
    update({ columns: [...sheet.columns, newColumn()] })
  }

  function removeColumn(uid: string) {
    update({ columns: sheet.columns.filter((c) => c._uid !== uid) })
  }

  function updateColumn(uid: string, patch: Partial<EditorColumn>) {
    update({
      columns: sheet.columns.map((c) => (c._uid === uid ? { ...c, ...patch } : c)),
    })
  }

  return (
    <div className="space-y-4 pt-2">
      <div className="flex flex-wrap items-end gap-4">
        <div className="grid gap-1.5">
          <Label>Nome da planilha</Label>
          <Input
            value={sheet.label}
            onChange={(e) => update({ label: e.target.value })}
            className="w-64"
          />
        </div>
        <div className="grid gap-1.5">
          <Label>Iniciar na linha</Label>
          <Input
            type="number"
            min={1}
            value={sheet.start_row}
            onChange={(e) => update({ start_row: parseInt(e.target.value, 10) || 1 })}
            className="w-28"
          />
        </div>
      </div>

      <PreviewTable />

      <div className="rounded-lg border">
        <div className="border-b bg-muted/40 px-3 py-2 text-sm font-medium">Campos</div>
        <div className="space-y-2 overflow-x-auto p-3">
          <div className={cn(COL_GRID, "px-1 text-xs font-medium text-muted-foreground")}>
            <span>Campo</span>
            <span className="text-center">Col.</span>
            <span>Transformações</span>
            <span className="text-center" title="Multiplicar por -1">
              ×(-1)
            </span>
            <span className="text-center" title="Pular linha se vazio">
              Vazio?
            </span>
            <span className="text-center" title="Pular se data inválida">
              Data?
            </span>
            <span className="text-center" title="Fallback débito/crédito → valor">
              Fb→valor
            </span>
            <span />
          </div>

          {sheet.columns.length === 0 && (
            <p className="px-1 py-2 text-sm text-muted-foreground">
              Nenhum campo configurado. Adicione ao menos um.
            </p>
          )}

          {sheet.columns.map((c) => (
            <ColumnRow
              key={c._uid}
              column={c}
              onChange={(patch) => updateColumn(c._uid, patch)}
              onRemove={() => removeColumn(c._uid)}
            />
          ))}

          <Button variant="outline" size="sm" onClick={addColumn} className="mt-1">
            <Plus className="size-4" />
            Adicionar campo
          </Button>
        </div>
      </div>
    </div>
  )
}
