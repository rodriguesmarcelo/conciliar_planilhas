import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { COL_GRID, CUSTOM_FIELD, FIELD_OPTIONS, type EditorColumn } from "./constants"
import { TransformDialog } from "./TransformDialog"

const KNOWN = FIELD_OPTIONS as readonly string[]

export function ColumnRow({
  column,
  onChange,
  onRemove,
}: {
  column: EditorColumn
  onChange: (patch: Partial<EditorColumn>) => void
  onRemove: () => void
}) {
  const isData = column.field === "data"
  const isKnown = KNOWN.includes(column.field)
  const selectValue = isKnown ? column.field : CUSTOM_FIELD

  function onFieldChange(value: string) {
    if (value === CUSTOM_FIELD) {
      onChange({ field: "", skip_if_invalid_date: false })
    } else {
      onChange({
        field: value,
        skip_if_invalid_date: value === "data" ? column.skip_if_invalid_date : false,
      })
    }
  }

  return (
    <div className={COL_GRID}>
      <div className="flex flex-col gap-1">
        <Select value={selectValue} onValueChange={(v) => onFieldChange(String(v))}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {FIELD_OPTIONS.map((f) => (
              <SelectItem key={f} value={f}>
                {f}
              </SelectItem>
            ))}
            <SelectItem value={CUSTOM_FIELD}>{CUSTOM_FIELD}</SelectItem>
          </SelectContent>
        </Select>
        {selectValue === CUSTOM_FIELD && (
          <Input
            value={column.field}
            placeholder="campo personalizado"
            onChange={(e) => onChange({ field: e.target.value })}
          />
        )}
      </div>

      <Input
        type="number"
        min={1}
        value={column.col_index}
        onChange={(e) => onChange({ col_index: parseInt(e.target.value, 10) || 0 })}
        className="text-center"
      />

      <TransformDialog
        value={column.transformations}
        onChange={(v) => onChange({ transformations: v })}
      />

      <div className="flex justify-center">
        <Checkbox
          checked={column.multiply_minus_one}
          onCheckedChange={(c) => onChange({ multiply_minus_one: Boolean(c) })}
        />
      </div>
      <div className="flex justify-center">
        <Checkbox
          checked={column.skip_if_empty}
          onCheckedChange={(c) => onChange({ skip_if_empty: Boolean(c) })}
        />
      </div>
      <div className="flex justify-center">
        <Checkbox
          checked={column.skip_if_invalid_date}
          disabled={!isData}
          onCheckedChange={(c) => onChange({ skip_if_invalid_date: Boolean(c) })}
        />
      </div>
      <div className="flex justify-center">
        <Checkbox
          checked={column.is_fallback_of === "valor"}
          onCheckedChange={(c) => onChange({ is_fallback_of: c ? "valor" : null })}
        />
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="text-destructive hover:text-destructive"
        onClick={onRemove}
        aria-label="Remover campo"
      >
        <X className="size-4" />
      </Button>
    </div>
  )
}
