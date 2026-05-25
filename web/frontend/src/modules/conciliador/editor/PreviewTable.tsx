import { useRef, useState } from "react"
import { toast } from "sonner"
import { FileSpreadsheet } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { preview, type PreviewResult } from "@/modules/conciliador/api"
import { XLS_MESSAGE } from "./constants"

export function PreviewTable() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const [result, setResult] = useState<PreviewResult | null>(null)
  const [loading, setLoading] = useState(false)

  async function onPick(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = "" // permite reselecionar o mesmo arquivo
    if (!file) return
    if (file.name.toLowerCase().endsWith(".xls")) {
      toast.error(XLS_MESSAGE)
      return
    }
    setFileName(file.name)
    setLoading(true)
    try {
      setResult(await preview(file))
    } catch (err) {
      toast.error((err as Error).message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3">
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.csv"
          className="hidden"
          onChange={onPick}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={() => inputRef.current?.click()}
          disabled={loading}
        >
          <FileSpreadsheet className="size-4" />
          Selecionar arquivo para pré-visualização
        </Button>
        <span className="truncate text-sm text-muted-foreground">
          {loading ? "Carregando…" : fileName ?? "Nenhum arquivo selecionado"}
        </span>
      </div>

      {result && result.header.length > 0 && (
        <div className="max-h-64 overflow-auto rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                {result.header.map((h, i) => (
                  <TableHead key={i} className="text-center font-mono">
                    {h}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {result.rows.map((row, ri) => (
                <TableRow key={ri}>
                  {row.map((cell, ci) => (
                    <TableCell key={ci} className="font-mono text-xs">
                      {cell}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}
