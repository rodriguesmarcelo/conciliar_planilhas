import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Copy, Pencil, Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  deleteProfile,
  duplicateProfile,
  listProfiles,
  type Profile,
} from "@/modules/conciliador/api"

const PROFILES_KEY = ["conciliador", "profiles"]

export default function Home() {
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data, isLoading, isError, error } = useQuery({
    queryKey: PROFILES_KEY,
    queryFn: listProfiles,
  })

  const dup = useMutation({
    mutationFn: duplicateProfile,
    onSuccess: (p) => {
      toast.success(`Perfil duplicado: ${p.name}`)
      qc.invalidateQueries({ queryKey: PROFILES_KEY })
    },
    onError: (e) => toast.error((e as Error).message),
  })

  const del = useMutation({
    mutationFn: deleteProfile,
    onSuccess: () => {
      toast.success("Perfil excluído")
      qc.invalidateQueries({ queryKey: PROFILES_KEY })
    },
    onError: (e) => toast.error((e as Error).message),
  })

  if (isLoading) return <p className="text-muted-foreground">Carregando perfis…</p>
  if (isError)
    return <p className="text-destructive">Erro ao carregar perfis: {(error as Error).message}</p>

  const profiles = data ?? []
  const busy = dup.isPending || del.isPending

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Conciliador de Planilhas</h1>
          <p className="text-muted-foreground">Selecione um perfil para executar, ou crie um novo.</p>
        </div>
        <Button onClick={() => navigate("/conciliador/profiles/new")}>
          <Plus className="size-4" /> Novo Perfil
        </Button>
      </div>

      {profiles.length === 0 ? (
        <div className="rounded-lg border border-dashed p-10 text-center text-muted-foreground">
          Nenhum perfil encontrado. Clique em “Novo Perfil” para criar um.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {profiles.map((p) => (
            <ProfileCard
              key={p.id}
              profile={p}
              busy={busy}
              onRun={() => navigate(`/conciliador/run/${p.id}`)}
              onEdit={() => navigate(`/conciliador/profiles/${p.id}/edit`)}
              onDuplicate={() => dup.mutate(p.id)}
              onDelete={() => del.mutate(p.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function ProfileCard({
  profile,
  busy,
  onRun,
  onEdit,
  onDuplicate,
  onDelete,
}: {
  profile: Profile
  busy: boolean
  onRun: () => void
  onEdit: () => void
  onDuplicate: () => void
  onDelete: () => void
}) {
  const nSheets = profile.sheets?.length ?? 0
  return (
    <Card
      role="button"
      tabIndex={0}
      onClick={onRun}
      onKeyDown={(e) => {
        if (e.key === "Enter") onRun()
      }}
      className="cursor-pointer gap-3 transition-colors hover:border-primary hover:bg-accent/40"
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="truncate">{profile.name}</CardTitle>
          <Badge variant={profile.mode === "dual" ? "default" : "secondary"}>
            {profile.mode === "dual" ? "Dual" : "Single"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        {nSheets} planilha{nSheets === 1 ? "" : "s"}
      </CardContent>
      <CardFooter className="gap-1" onClick={(e) => e.stopPropagation()}>
        <Button variant="ghost" size="sm" onClick={onEdit}>
          <Pencil className="size-4" /> Editar
        </Button>
        <Button variant="ghost" size="sm" onClick={onDuplicate} disabled={busy}>
          <Copy className="size-4" /> Duplicar
        </Button>
        <DeleteProfileButton name={profile.name} busy={busy} onConfirm={onDelete} />
      </CardFooter>
    </Card>
  )
}

function DeleteProfileButton({
  name,
  busy,
  onConfirm,
}: {
  name: string
  busy: boolean
  onConfirm: () => void
}) {
  const [open, setOpen] = useState(false)
  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger
        render={
          <Button
            variant="ghost"
            size="icon"
            className="ml-auto text-destructive hover:text-destructive"
            disabled={busy}
            aria-label="Excluir"
          />
        }
      >
        <Trash2 className="size-4" />
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Excluir perfil</AlertDialogTitle>
          <AlertDialogDescription>
            Deseja realmente excluir o perfil “{name}”? Esta ação não pode ser desfeita.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <AlertDialogAction
            className="bg-destructive text-white hover:bg-destructive/90"
            onClick={() => {
              onConfirm()
              setOpen(false)
            }}
          >
            Excluir
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
