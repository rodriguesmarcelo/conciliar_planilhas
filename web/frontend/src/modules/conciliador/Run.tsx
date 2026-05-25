import { useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import { ArrowLeft, CheckCircle2, Download, Loader2, Play, RotateCcw } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  getProfile,
  resultUrl,
  runReconciliation,
  type RunResult,
} from "@/modules/conciliador/api"
import { FileDropField } from "@/modules/conciliador/FileDropField"

export default function Run() {
  const { id } = useParams()
  const navigate = useNavigate()

  const {
    data: profile,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["conciliador", "profile", id],
    queryFn: () => getProfile(id!),
    enabled: Boolean(id),
  })

  const [fileA, setFileA] = useState<File | null>(null)
  const [fileB, setFileB] = useState<File | null>(null)
  const [result, setResult] = useState<RunResult | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const run = useMutation({
    mutationFn: () => runReconciliation(id!, fileA!, fileB ?? undefined),
    onMutate: () => {
      setErrorMsg(null)
      setResult(null)
    },
    onSuccess: (r) => {
      setResult(r)
      toast.success("Conciliação concluída!")
    },
    onError: (e) => setErrorMsg((e as Error).message),
  })

  if (isLoading) return <p className="text-muted-foreground">Carregando perfil…</p>
  if (isError || !profile)
    return (
      <p className="text-destructive">
        Erro ao carregar perfil: {(error as Error)?.message ?? "não encontrado"}
      </p>
    )

  const isDual = profile.mode === "dual"
  const sheets = profile.sheets ?? []
  const labelA = sheets[0]?.label || "Planilha A"
  const labelB = sheets[1]?.label || "Planilha B"
  const missingFiles = !fileA || (isDual && !fileB)

  function reset() {
    setFileA(null)
    setFileB(null)
    setResult(null)
    setErrorMsg(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="outline" size="sm" onClick={() => navigate("/conciliador")}>
          <ArrowLeft className="size-4" /> Voltar
        </Button>
        <h1 className="text-2xl font-semibold">Executar Conciliação — {profile.name}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Arquivos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <FileDropField
            label={`Planilha A — ${labelA}`}
            file={fileA}
            onFile={setFileA}
            disabled={run.isPending}
          />
          {isDual && (
            <FileDropField
              label={`Planilha B — ${labelB}`}
              file={fileB}
              onFile={setFileB}
              disabled={run.isPending}
            />
          )}
        </CardContent>
      </Card>

      <Button
        size="lg"
        className="w-full"
        disabled={missingFiles || run.isPending}
        onClick={() => run.mutate()}
      >
        {run.isPending ? (
          <>
            <Loader2 className="size-4 animate-spin" /> Processando…
          </>
        ) : (
          <>
            <Play className="size-4" /> Executar Conciliação
          </>
        )}
      </Button>

      {errorMsg && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm whitespace-pre-line text-destructive">
          {errorMsg}
        </div>
      )}

      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-emerald-600">
              <CheckCircle2 className="size-5" /> Conciliação concluída
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1 rounded-lg border bg-muted/40 p-4 text-sm">
              {result.mode === "single" ? (
                <CountRow label="Registros normalizados" value={result.counts.normalizados ?? 0} good />
              ) : (
                <>
                  <CountRow label="Registros conciliados" value={result.counts.conciliados ?? 0} good />
                  <CountRow
                    label={`Não conciliados (${labelA})`}
                    value={result.counts.nao_conciliados_a ?? 0}
                  />
                  <CountRow
                    label={`Não conciliados (${labelB})`}
                    value={result.counts.nao_conciliados_b ?? 0}
                  />
                </>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              <Button render={<a href={resultUrl(result.download_token)} download />}>
                <Download className="size-4" /> Baixar resultado
              </Button>
              <Button variant="outline" onClick={reset}>
                <RotateCcw className="size-4" /> Nova conciliação
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function CountRow({ label, value, good = false }: { label: string; value: number; good?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-muted-foreground">{label}</span>
      <span
        className={cn(
          "font-semibold tabular-nums",
          good ? "text-emerald-600" : value > 0 ? "text-destructive" : "text-foreground",
        )}
      >
        {value}
      </span>
    </div>
  )
}
