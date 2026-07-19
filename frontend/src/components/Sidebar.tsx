/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Badge } from 'components/ui/badge';
import { Button } from 'components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from 'components/ui/card';
import { Separator } from 'components/ui/separator';
import { cn } from 'lib/utils';
import { Screen } from '../types';

interface SidebarProps {
  currentScreen: Screen;
  onNavigate: (screen: Screen) => void;
  onLogout: () => void;
}

type NavItem = {
  screen: Screen;
  label: string;
  description: string;
  icon: string;
  badge?: string;
};

const menuItems: NavItem[] = [
  {
    screen: Screen.DASHBOARD,
    label: 'Dashboard',
    description: 'Live command view',
    icon: 'dashboard',
    badge: 'Live',
  },
  {
    screen: Screen.CHAT,
    label: 'Intelligence Chat',
    description: 'Ask the FIR database',
    icon: 'forum',
  },
  {
    screen: Screen.NETWORK,
    label: 'Network Explorer',
    description: 'Co-accused links',
    icon: 'hub',
  },
  {
    screen: Screen.ANALYTICS,
    label: 'Analytics',
    description: 'Patterns and risk',
    icon: 'analytics',
  },
];

function MaterialIcon({
  children,
  active = false,
}: {
  children: string;
  active?: boolean;
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'material-symbols-outlined flex size-8 shrink-0 items-center justify-center rounded-md border border-border bg-muted text-[19px] text-muted-foreground transition-colors',
        active && 'border-primary/40 bg-primary/15 text-primary'
      )}
      data-icon="inline-start"
      style={{ fontVariationSettings: active ? '"FILL" 1' : undefined }}
    >
      {children}
    </span>
  );
}

export default function Sidebar({ currentScreen, onNavigate, onLogout }: SidebarProps) {
  return (
    <aside className="fixed left-0 top-0 z-10 hidden h-full w-64 shrink-0 border-r border-border bg-background/95 text-foreground md:flex">
      <nav aria-label="Primary navigation" className="flex min-h-0 w-full flex-col">
        <div className="p-4">
          <Card className="border-border/80 bg-card/90 shadow-none">
            <CardHeader className="gap-0 p-4">
              <div className="flex items-center gap-3">
                <div className="flex size-11 items-center justify-center rounded-lg border border-primary/30 bg-primary/10 text-primary">
                  <span
                    aria-hidden="true"
                    className="material-symbols-outlined text-[24px]"
                    style={{ fontVariationSettings: '"FILL" 1' }}
                  >
                    security
                  </span>
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
            <CardContent className="px-4 pb-4">
              <div className="flex items-center justify-between gap-2 rounded-md border border-border bg-muted/40 px-2.5 py-2">
                <span className="font-mono text-[10px] font-medium text-muted-foreground">
                  SESSION
                </span>
                <Badge variant="secondary" className="rounded-md font-mono text-[10px]">
                  Active
                </Badge>
              </div>
            </CardContent>
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
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={cn(
                    'h-auto w-full justify-start rounded-lg px-2.5 py-2.5 text-left',
                    isActive && 'bg-accent text-accent-foreground ring-1 ring-primary/25'
                  )}
                  onClick={() => onNavigate(item.screen)}
                >
                  <MaterialIcon active={isActive}>{item.icon}</MaterialIcon>
                  <span className="flex min-w-0 flex-1 flex-col items-start gap-0.5">
                    <span className="flex w-full items-center justify-between gap-2">
                      <span className="truncate text-sm font-semibold leading-none">
                        {item.label}
                      </span>
                      {item.badge && (
                        <Badge
                          variant={isActive ? 'default' : 'outline'}
                          className="rounded-md font-mono text-[10px]"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </span>
                    <span className="truncate text-[11px] font-normal leading-4 text-muted-foreground">
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
                <span aria-hidden="true" className="material-symbols-outlined text-[20px] text-muted-foreground">
                  account_circle
                </span>
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
            <Button type="button" variant="outline" className="justify-start">
              <span aria-hidden="true" className="material-symbols-outlined" data-icon="inline-start">
                settings
              </span>
              Settings
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="justify-start"
              onClick={onLogout}
            >
              <span aria-hidden="true" className="material-symbols-outlined" data-icon="inline-start">
                logout
              </span>
              Logout
            </Button>
          </div>
        </div>
      </nav>
    </aside>
  );
}
