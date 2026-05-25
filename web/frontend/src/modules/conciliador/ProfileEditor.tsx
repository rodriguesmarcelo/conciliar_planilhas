import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { ArrowLeft, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { getProfile, saveProfile, type ProfilePayload } from "@/modules/conciliador/api"
import { SheetPanel } from "@/modules/conciliador/editor/SheetPanel"
import {
  DATE_FORMATS,
  INVALID_FILENAME_CHARS,
  MATCH_FIELDS,
  newSheet,
  stripSheet,
  toEditorSheet,
  type EditorSheet,
} from "@/modules/conciliador/editor/constants"

const PROFILES_KEY = ["conciliador", "profiles"]

function sheetLabel(i: number): string {
  return `Planilha ${i === 0 ? "A" : "B"}`
}

function titleCase(s: string): string {
  return s
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ")
}

export default function ProfileEditor() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: loaded, isLoading } = useQuery({
    queryKey: ["conciliador", "profile", id],
    queryFn: () => getProfile(id!),
    enabled: isEdit,
  })

  const [name, setName] = useState("")
  const [mode, setMode] = useState<"dual" | "single">("dual")
  const [dateFormat, setDateFormat] = useState("dd/mm/yyyy")
  const [matchFields, setMatchFields] = useState<string[]>([])
  const [oneToOne, setOneToOne] = useState(false)
  const [sheets, setSheets] = useState<EditorSheet[]>(() => [
    newSheet(sheetLabel(0)),
    newSheet(sheetLabel(1)),
  ])
  const [activeTab, setActiveTab] = useState("0")
  const [prefilled, setPrefilled] = useState(false)

  useEffect(() => {
    if (!loaded || prefilled) return
    const m = loaded.mode === "single" ? "single" : "dual"
    setName(loaded.name ?? "")
    setMode(m)
    setDateFormat(loaded.date_format ?? "dd/mm/yyyy")
    setMatchFields(loaded.comparison?.match_fields ?? [])
    setOneToOne(loaded.comparison?.one_to_one ?? false)

    const es = (loaded.sheets ?? []).map(toEditorSheet)
    if (m === "single") {
      setSheets([es[0] ?? newSheet("Planilha")])
    } else {
      setSheets(es.length >= 2 ? es : [es[0] ?? newSheet(sheetLabel(0)), newSheet(sheetLabel(1))])
    }
    setActiveTab("0")
    setPrefilled(true)
  }, [loaded, prefilled])

  function onModeChange(next: string) {
    const m = next === "single" ? "single" : "dual"
    setMode(m)
    setSheets((prev) => {
      if (m === "single") return [prev[0] ?? newSheet("Planilha")]
      if (prev.length >= 2) return prev
      return [prev[0] ?? newSheet(sheetLabel(0)), newSheet(sheetLabel(1))]
    })
    setActiveTab("0")
  }

  function toggleMatch(f: string) {
    setMatchFields((prev) => (prev.includes(f) ? prev.filter((x) => x !== f) : [...prev, f]))
  }

  function updateSheet(i: number, next: EditorSheet) {
    setSheets((prev) => prev.map((s, idx) => (idx === i ? next : s)))
  }

  function validate(): string | null {
    const trimmed = name.trim()
    if (!trimmed) return "O nome do perfil não pode estar vazio."
    const bad = [...trimmed].filter((c) => INVALID_FILENAME_CHARS.includes(c))
    if (bad.length) {
      const uniq = [...new Set(bad)]
        .sort()
        .map((c) => `'${c}'`)
        .join("  ")
      return `O nome do perfil contém caracteres inválidos: ${uniq}`
    }
    for (let i = 0; i < sheets.length; i++) {
      const s = sheets[i]
      if (s.columns.length === 0) {
        return `A planilha '${s.label || sheetLabel(i)}' deve ter ao menos 1 campo configurado.`
      }
      for (const c of s.columns) {
        if (!Number.isInteger(c.col_index) || c.col_index < 1) {
          return `Índice de coluna inválido no campo '${c.field}'.`
        }
      }
    }
    return null
  }

  const save = useMutation({
    mutationFn: (payload: ProfilePayload) => saveProfile(payload),
    onSuccess: (p) => {
      toast.success(`Perfil '${p.name}' salvo com sucesso!`)
      qc.invalidateQueries({ queryKey: PROFILES_KEY })
      navigate("/conciliador")
    },
    onError: (e) => toast.error((e as Error).message),
  })

  function onSubmit() {
    const err = validate()
    if (err) {
      toast.error(err)
      return
    }
    const payload: ProfilePayload = {
      ...(isEdit && loaded ? { id: loaded.id } : {}),
      name: name.trim(),
      mode,
      date_format: dateFormat,
      sheets: sheets.map(stripSheet),
      comparison: {
        match_fields: mode === "single" ? [] : matchFields,
        one_to_one: mode === "single" ? false : oneToOne,
      },
    }
    save.mutate(payload)
  }

  if (isEdit && isLoading) {
    return <p className="text-muted-foreground">Carregando perfil…</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="outline" size="sm" onClick={() => navigate("/conciliador")}>
          <ArrowLeft className="size-4" /> Voltar
        </Button>
        <h1 className="text-2xl font-semibold">{isEdit ? "Editar perfil" : "Novo perfil"}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Geral</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid max-w-md gap-1.5">
            <Label htmlFor="profile-name">Nome do perfil</Label>
            <Input
              id="profile-name"
              value={name}
              placeholder="Ex: Razão × Extrato"
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="grid gap-1.5">
            <Label>Modo</Label>
            <RadioGroup
              value={mode}
              onValueChange={(v) => onModeChange(String(v))}
              className="flex gap-6"
            >
              <div className="flex items-center gap-2">
                <RadioGroupItem id="mode-dual" value="dual" />
                <label htmlFor="mode-dual" className="text-sm select-none">
                  Duas planilhas
                </label>
              </div>
              <div className="flex items-center gap-2">
                <RadioGroupItem id="mode-single" value="single" />
                <label htmlFor="mode-single" className="text-sm select-none">
                  Uma planilha
                </label>
              </div>
            </RadioGroup>
          </div>

          <div className="grid gap-1.5">
            <Label>Formato de data</Label>
            <Select value={dateFormat} onValueChange={(v) => setDateFormat(String(v))}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DATE_FORMATS.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {mode === "dual" && (
        <Card>
          <CardHeader>
            <CardTitle>Comparação</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-x-6 gap-y-2">
              {MATCH_FIELDS.map((f) => (
                <div key={f} className="flex items-center gap-2">
                  <Checkbox
                    id={`match-${f}`}
                    checked={matchFields.includes(f)}
                    onCheckedChange={() => toggleMatch(f)}
                  />
                  <label htmlFor={`match-${f}`} className="text-sm select-none">
                    {titleCase(f)}
                  </label>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="one-to-one"
                checked={oneToOne}
                onCheckedChange={(c) => setOneToOne(Boolean(c))}
              />
              <label htmlFor="one-to-one" className="text-sm select-none">
                Conciliação Um-para-Um (recomendado para cheques)
              </label>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Planilhas</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(String(v))}>
            <TabsList>
              {sheets.map((s, i) => (
                <TabsTrigger key={s._uid} value={String(i)}>
                  {s.label || sheetLabel(i)}
                </TabsTrigger>
              ))}
            </TabsList>
            {sheets.map((s, i) => (
              <TabsContent key={s._uid} value={String(i)}>
                <SheetPanel sheet={s} onChange={(next) => updateSheet(i, next)} />
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => navigate("/conciliador")}>
          Cancelar
        </Button>
        <Button onClick={onSubmit} disabled={save.isPending}>
          <Save className="size-4" /> Salvar perfil
        </Button>
      </div>
    </div>
  )
}
