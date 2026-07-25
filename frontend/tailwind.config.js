const { COLORS } = require('./src/constants/colors.js');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // shadcn semantic tokens
        'foreground':            'hsl(var(--foreground) / <alpha-value>)',
        'card':                  'hsl(var(--card) / <alpha-value>)',
        'card-foreground':       'hsl(var(--card-foreground) / <alpha-value>)',
        'popover':               'hsl(var(--popover) / <alpha-value>)',
        'popover-foreground':    'hsl(var(--popover-foreground) / <alpha-value>)',
        'primary-foreground':    'hsl(var(--primary-foreground) / <alpha-value>)',
        'secondary-foreground':  'hsl(var(--secondary-foreground) / <alpha-value>)',
        'muted':                 'hsl(var(--muted) / <alpha-value>)',
        'muted-foreground':      'hsl(var(--muted-foreground) / <alpha-value>)',
        'accent':                'hsl(var(--accent) / <alpha-value>)',
        'accent-foreground':     'hsl(var(--accent-foreground) / <alpha-value>)',
        'destructive':           'hsl(var(--destructive) / <alpha-value>)',
        'destructive-foreground':'hsl(var(--destructive-foreground) / <alpha-value>)',
        'border':                'hsl(var(--border) / <alpha-value>)',
        'input':                 'hsl(var(--input) / <alpha-value>)',
        'ring':                  'hsl(var(--ring) / <alpha-value>)',

        // Core surface tokens (dark tactical palette)
        'background':            'hsl(var(--background) / <alpha-value>)',
        'surface':               COLORS.surface.panel,
        'surface-variant':       COLORS.surface.container,
        'surface-container':     COLORS.surface.container,
        'surface-container-low': COLORS.surface.containerLow,
        'surface-container-high':COLORS.surface.containerHigh,
        'surface-container-highest': COLORS.surface.containerHighest,
        'panel':                 COLORS.surface.panel,

        // Primary (blue)
        'primary':               'hsl(var(--primary) / <alpha-value>)',
        'primary-container':     COLORS.primary.main,
        'primary-fixed':         COLORS.primary.fixed,
        'inverse-primary':       COLORS.primary.hover,
        'on-primary':            COLORS.text.white,
        'on-primary-container':  COLORS.text.white,

        // Secondary
        'secondary':             'hsl(var(--secondary) / <alpha-value>)',
        'secondary-container':   COLORS.primary.container,
        'on-secondary':          COLORS.text.white,

        // Tertiary (orange/amber warnings)
        'tertiary':              COLORS.status.warning,
        'tertiary-container':    '#7A5200',
        'on-tertiary':           COLORS.text.white,
        'on-tertiary-container': '#FFE0B2',

        // Error (red)
        'error':                 COLORS.status.error,
        'error-container':       COLORS.status.errorContainer,
        'on-error':              COLORS.text.white,
        'on-error-container':    '#FFB4AB',

        // On-surface hierarchy
        'on-surface':            COLORS.text.primary,
        'on-surface-variant':    COLORS.text.secondary,
        'on-primary-fixed':      COLORS.primary.fixed,

        // Borders
        'outline':               COLORS.border.default,
        'outline-variant':       COLORS.border.variant,
        'tactical':              COLORS.border.tactical,

        // Layout aliases
        'layout-bg':             COLORS.background.dark,
        'layout-surface':        COLORS.surface.panel,
        'layout-border':         COLORS.border.tactical,
      },
      fontFamily: {
        sans:  ['Inter', 'system-ui', 'sans-serif'],
        mono:  ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      spacing: {
        'xs':  '4px',
        'sm':  '8px',
        'md':  '16px',
        'lg':  '24px',
        'xl':  '32px',
        'gutter':          '16px',
        'margin-desktop':  '24px',
      },
      borderRadius: {
        'DEFAULT': 'var(--radius)',
        'sm': 'calc(var(--radius) - 4px)',
        'md': 'calc(var(--radius) - 2px)',
        'lg': 'var(--radius)',
        'xl': 'calc(var(--radius) + 4px)',
        'btn':     'var(--radius)',
        'card':    'calc(var(--radius) + 2px)',
      },
    },
  },
  plugins: [],
};
