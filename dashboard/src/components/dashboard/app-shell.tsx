import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  BellRing,
  BrainCircuit,
  ChartNoAxesCombined,
  CircleGauge,
  Database,
  ListFilter,
  Search,
  Settings,
  ShieldCheck,
  WalletCards,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { ReactNode } from "react";

const nav = [
  { label: "Executive Overview", to: "/", icon: CircleGauge },
  { label: "Transactions", to: "/transactions", icon: WalletCards },
  { label: "Analytics", to: "/analytics", icon: ChartNoAxesCombined },
  { label: "ML Models", to: "/ml-models", icon: BrainCircuit },
  { label: "Risk & Investigation", to: "/risk-investigation", icon: ShieldCheck },
  { label: "Alerts", to: "/alerts", icon: BellRing },
  { label: "Settings", to: "/settings", icon: Settings },
] as const;
function AppSidebar() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  return (
    <Sidebar collapsible="icon" className="border-sidebar-border">
      <SidebarHeader className="h-20 justify-center px-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className="grid size-10 shrink-0 place-items-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground shadow-lg">
            <Activity className="size-5" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <div className="truncate font-display text-sm font-bold text-sidebar-foreground">
                UPI Risk Monitor
              </div>
              <div className="text-[10px] uppercase text-sidebar-foreground/55">
                Anomaly intelligence
              </div>
            </div>
          )}
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {nav.map((item) => (
                <SidebarMenuItem key={item.to}>
                  <SidebarMenuButton
                    asChild
                    isActive={path === item.to}
                    tooltip={item.label}
                    className="h-10"
                  >
                    <Link to={item.to}>
                      <item.icon />
                      <span>{item.label}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="p-3">
        <div className="flex items-center gap-2 rounded-md border border-sidebar-border bg-sidebar-accent/50 p-2 text-xs">
          <Database className="size-4 shrink-0 text-sidebar-primary" />
          {!collapsed && (
            <span className="text-sidebar-foreground/70">Data · Jan–Jun 2024</span>
          )}
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <SidebarProvider>
      <div className="app-shell flex min-h-svh w-full">
        <AppSidebar />
        <SidebarInset className="min-w-0 bg-background soft-grid md:my-2 md:mr-2 md:rounded-lg md:shadow-2xl">
          <header className="sticky top-0 z-20 grid h-16 grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b bg-card/85 px-4 backdrop-blur-xl sm:px-6">
            <div className="flex min-w-0 items-center gap-3">
              <SidebarTrigger />
              <div className="relative hidden w-full max-w-sm sm:block">
                <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  aria-label="Global search"
                  placeholder="Search transactions, signals…"
                  className="bg-background pl-9"
                />
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <div className="hidden items-center gap-2 rounded-md border bg-background px-3 py-2 text-xs text-muted-foreground lg:flex">
                <span className="size-2 rounded-full bg-success" />
                Data source: PostgreSQL • Jan–Jun 2024
              </div>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link
                    to="/alerts"
                    aria-label="Open risk alerts"
                    className="relative grid size-9 place-items-center rounded-md border bg-background text-foreground hover:bg-accent"
                  >
                    <BellRing className="size-4" />
                    <span className="absolute -right-1 -top-1 grid size-4 place-items-center rounded-full bg-critical text-[9px] text-primary-foreground">
                      4
                    </span>
                  </Link>
                </TooltipTrigger>
                <TooltipContent>Risk/anomaly alerts</TooltipContent>
              </Tooltip>
            </div>
          </header>
          <main className="min-w-0 flex-1 p-4 pb-24 sm:p-6 lg:p-8">{children}</main>
          <footer className="border-t bg-card/80 px-4 py-3 text-center text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">Responsible use:</span> Anomaly signals
            indicate unusual transaction behavior and do not represent confirmed fraud.
          </footer>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
