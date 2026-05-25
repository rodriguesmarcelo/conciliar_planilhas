import { Route, Routes } from "react-router-dom"
import Home from "@/modules/conciliador/Home"
import ProfileEditor from "@/modules/conciliador/ProfileEditor"
import RunPlaceholder from "@/modules/conciliador/RunPlaceholder"

export default function ConciliadorModule() {
  return (
    <Routes>
      <Route index element={<Home />} />
      <Route path="profiles/new" element={<ProfileEditor />} />
      <Route path="profiles/:id/edit" element={<ProfileEditor />} />
      <Route path="run/:id" element={<RunPlaceholder />} />
    </Routes>
  )
}
