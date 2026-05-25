import { Route, Routes } from "react-router-dom"
import Home from "@/modules/conciliador/Home"
import EditorPlaceholder from "@/modules/conciliador/EditorPlaceholder"
import RunPlaceholder from "@/modules/conciliador/RunPlaceholder"

export default function ConciliadorModule() {
  return (
    <Routes>
      <Route index element={<Home />} />
      <Route path="profiles/new" element={<EditorPlaceholder />} />
      <Route path="profiles/:id/edit" element={<EditorPlaceholder />} />
      <Route path="run/:id" element={<RunPlaceholder />} />
    </Routes>
  )
}
