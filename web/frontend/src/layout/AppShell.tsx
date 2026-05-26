import { Link, NavLink, Outlet } from "react-router-dom"
import { MODULES } from "@/modules/registry"
import { AppIcon } from "@/components/AppIcon"
import { cn } from "@/lib/utils"
import logoBarelli from "@/assets/logo-barelli.png"

export function AppShell() {
  return (
    <div className="min-h-svh">
      {/* Topbar */}
      <header className="fixed inset-x-0 top-0 z-20 flex h-14 items-center border-b bg-background px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <img
            src={logoBarelli}
            alt="Barelli"
            className="size-7 object-contain"
          />
          <span>barelli.automacao</span>
        </Link>
      </header>

      {/* Sidebar */}
      <aside className="fixed bottom-0 left-0 top-14 z-10 w-60 border-r bg-sidebar text-sidebar-foreground">
        <nav className="flex flex-col gap-1 p-3">
          <NavItem to="/" icon="layout-grid" label="Hub" end />
          {MODULES.map((m) => (
            <NavItem key={m.id} to={m.basePath} icon={m.icon} label={m.title} />
          ))}
        </nav>
      </aside>

      {/* Conteúdo */}
      <main className="pt-14 pl-60">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

function NavItem({
  to,
  icon,
  label,
  end,
}: {
  to: string
  icon: string
  label: string
  end?: boolean
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
          isActive
            ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
            : "hover:bg-sidebar-accent/50",
        )
      }
    >
      <AppIcon name={icon} className="size-4" />
      <span className="truncate">{label}</span>
    </NavLink>
  )
}
