/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  LayoutDashboard,
  MessageSquareText,
  Network,
  LineChart,
  User,
  Settings as SettingsIcon,
  LogOut,
  LucideIcon,
} from "lucide-react";
import { Badge } from "components/ui/badge";
import { Button } from "components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "components/ui/card";
import { Separator } from "components/ui/separator";
import { cn } from "lib/utils";
import { Screen } from "../types";
import { COLORS } from "../constants/colors";

interface SidebarProps {
  currentScreen: Screen;
  onNavigate: (screen: Screen) => void;
  onLogout: () => void;
}

type NavItem = {
  screen: Screen;
  label: string;
  description: string;
  icon: LucideIcon;
  badge?: string;
};

const menuItems: NavItem[] = [
  {
    screen: Screen.DASHBOARD,
    label: "Dashboard",
    description: "Live command view",
    icon: LayoutDashboard,
    badge: "Live",
  },
  {
    screen: Screen.CHAT,
    label: "Intelligence Chat",
    description: "Ask the FIR database",
    icon: MessageSquareText,
  },
  {
    screen: Screen.NETWORK,
    label: "Network Explorer",
    description: "Co-accused links",
    icon: Network,
  },
  {
    screen: Screen.ANALYTICS,
    label: "Analytics",
    description: "Patterns and risk",
    icon: LineChart,
  },
];

function NavVectorIcon({
  icon: Icon,
  active = false,
}: {
  icon: LucideIcon;
  active?: boolean;
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-md border transition-colors",
      )}
      style={
        active
          ? {
              backgroundColor: `${COLORS.primary.main}22`,
              borderColor: `${COLORS.primary.main}55`,
              color: COLORS.primary.main,
            }
          : {
              backgroundColor: "rgba(255,255,255,0.05)",
              borderColor: "rgba(255,255,255,0.1)",
              color: COLORS.text.muted,
            }
      }
      data-icon="inline-start"
    >
      <Icon className="size-[18px] stroke-[2]" />
    </span>
  );
}

export default function Sidebar({
  currentScreen,
  onNavigate,
  onLogout,
}: SidebarProps) {
  return (
    <aside
      className="fixed left-0 top-0 z-10 hidden h-full w-64 shrink-0 border-r text-foreground md:flex"
      style={{
        backgroundColor: COLORS.surface.panel,
        borderColor: COLORS.border.default,
      }}
    >
      <nav
        aria-label="Primary navigation"
        className="flex min-h-0 w-full flex-col"
      >
        <div className="p-4">
          <Card>
            <CardHeader className="gap-0 p-4">
              <div className="flex items-center gap-3">
                <div className="flex size-11 items-center justify-center rounded-lg ">
                  <img
                    src="/logo.svg"
                    alt="PRISM Logo"
                    className="h-7 w-7 object-contain"
                  />
                </div>
                <div className="min-w-0">
                  <CardTitle className="font-mono text-[22px] font-bold tracking-[0] text-foreground">
                    PRISM
                  </CardTitle>
                  <CardDescription className="mt-0 font-mono text-[11px]">
                    Operations monitor
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </div>

        <Separator />

        <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto p-3 custom-scrollbar">
          <div className="px-2 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Workspace
          </div>

          <div className="flex flex-col gap-1">
            {menuItems.map((item) => {
              const isActive = currentScreen === item.screen;

              return (
                <Button
                  key={item.screen}
                  type="button"
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "h-auto w-full justify-start rounded-lg px-2.5 py-2.5 text-left",
                  )}
                  style={
                    isActive
                      ? {
                          backgroundColor: `${COLORS.primary.main}18`,
                          boxShadow: `inset 0 0 0 1px ${COLORS.primary.main}40`,
                        }
                      : {}
                  }
                  onClick={() => onNavigate(item.screen)}
                >
                  <NavVectorIcon icon={item.icon} active={isActive} />
                  <span className="flex min-w-0 flex-1 flex-col items-start gap-0.5">
                    <span className="flex w-full items-center justify-between gap-2">
                      <span
                        className="truncate text-sm font-semibold leading-none"
                        style={{
                          color: isActive
                            ? COLORS.primary.light
                            : COLORS.text.primary,
                        }}
                      >
                        {item.label}
                      </span>
                      {item.badge && (
                        <Badge
                          variant={isActive ? "default" : "outline"}
                          className="rounded-md font-mono text-[10px]"
                          style={
                            isActive
                              ? {
                                  backgroundColor: COLORS.primary.main,
                                  color: "#fff",
                                  borderColor: "transparent",
                                }
                              : {}
                          }
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </span>
                    <span
                      className="truncate text-[11px] font-normal leading-4"
                      style={{
                        color: isActive
                          ? `${COLORS.primary.light}99`
                          : COLORS.text.muted,
                      }}
                    >
                      {item.description}
                    </span>
                  </span>
                </Button>
              );
            })}
          </div>
        </div>

        <Separator />

        <div className="flex flex-col gap-3 p-3">
          <Card className="border-border bg-card/80 shadow-none">
            <CardContent className="flex items-center gap-3 p-3">
              <div className="flex size-9 items-center justify-center rounded-md border border-border bg-muted">
                <User className="size-4 text-muted-foreground" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-semibold text-foreground">
                  Command user
                </div>
                <div className="truncate font-mono text-[10px] text-muted-foreground">
                  Analyst access
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-2 gap-2">
            <Button type="button" variant="outline" className="justify-start gap-2">
              <SettingsIcon className="size-4" />
              Settings
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="justify-start gap-2"
              onClick={onLogout}
            >
              <LogOut className="size-4" />
              Logout
            </Button>
          </div>
        </div>
      </nav>
    </aside>
  );
}
