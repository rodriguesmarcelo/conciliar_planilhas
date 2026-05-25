import { useRef, useState } from "react"
import { toast } from "sonner"
import { FileSpreadsheet, Upload, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { XLS_MESSAGE } from "@/modules/conciliador/editor/constants"

export function FileDropField({
  label,
  file,
  onFile,
  disabled = false,
}: {
  label: string
  file: File | null
  onFile: (f: File | null) => void
  disabled?: boolean
}) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function accept(f: File | undefined) {
    if (!f) return
    if (f.name.toLowerCase().endsWith(".xls")) {
      toast.error(XLS_MESSAGE)
      return
    }
    onFile(f)
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    accept(e.dataTransfer.files?.[0])
  }

  return (
    <div className="space-y-1.5">
      <p className="text-sm font-medium">{label}</p>
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.csv"
        className="hidden"
        onChange={(e) => {
          accept(e.target.files?.[0])
          e.target.value = ""
        }}
      />
      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-disabled={disabled}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => {
          if (!disabled && (e.key === "Enter" || e.key === " ")) {
            e.preventDefault()
            inputRef.current?.click()
          }
        }}
        onDragOver={(e) => {
          e.preventDefault()
          if (!disabled) setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          "flex items-center gap-3 rounded-lg border border-dashed px-4 py-5 text-sm transition-colors outline-none",
          disabled
            ? "cursor-not-allowed opacity-50"
            : "cursor-pointer hover:border-primary hover:bg-accent/40 focus-visible:border-primary",
          dragging && "border-primary bg-accent/60",
        )}
      >
        {file ? (
          <>
            <FileSpreadsheet className="size-5 shrink-0 text-primary" />
            <span className="flex-1 truncate font-medium">{file.name}</span>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Remover arquivo"
              disabled={disabled}
              onClick={(e) => {
                e.stopPropagation()
                onFile(null)
              }}
            >
              <X className="size-4" />
            </Button>
          </>
        ) : (
          <>
            <Upload className="size-5 shrink-0 text-muted-foreground" />
            <span className="text-muted-foreground">
              Arraste o arquivo aqui ou clique para selecionar (.xlsx, .csv)
            </span>
          </>
        )}
      </div>
    </div>
  )
}
