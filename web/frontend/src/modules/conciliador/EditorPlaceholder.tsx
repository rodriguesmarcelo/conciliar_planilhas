import { useParams } from "react-router-dom"

export default function EditorPlaceholder() {
  const { id } = useParams()
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold">{id ? "Editar perfil" : "Novo perfil"}</h1>
      <p className="text-muted-foreground">
        Editor em construção (Task 05){id ? ` — id: ${id}` : ""}.
      </p>
    </div>
  )
}
