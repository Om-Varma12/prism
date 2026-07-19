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
        'surface':               '#111318',
        'surface-variant':       '#1A1D24',
        'surface-container':     '#1A1D24',
        'surface-container-low': '#141720',
        'surface-container-high':'#252830',
        'surface-container-highest': '#2E3138',
        'panel':                 '#111318',

        // Primary (blue)
        'primary':               'hsl(var(--primary) / <alpha-value>)',
        'primary-container':     '#3B6FE8',
        'primary-fixed':         '#A8C4FF',
        'inverse-primary':       '#2b5bc2',
        'on-primary':            '#FFFFFF',
        'on-primary-container':  '#FFFFFF',

        // Secondary
        'secondary':             'hsl(var(--secondary) / <alpha-value>)',
        'secondary-container':   '#2A3A6E',
        'on-secondary':          '#FFFFFF',

        // Tertiary (orange/amber warnings)
        'tertiary':              '#E8A030',
        'tertiary-container':    '#7A5200',
        'on-tertiary':           '#FFFFFF',
        'on-tertiary-container': '#FFE0B2',

        // Error (red)
        'error':                 '#FF4D4D',
        'error-container':       '#93000A',
        'on-error':              '#FFFFFF',
        'on-error-container':    '#FFB4AB',

        // On-surface hierarchy
        'on-surface':            '#E2E2E5',
        'on-surface-variant':    '#8B92A5',
        'on-primary-fixed':      '#A8C4FF',

        // Borders
        'outline':               '#4A5060',
        'outline-variant':       '#252830',
        'tactical':              '#252830',

        // Layout aliases
        'layout-bg':             '#0A0C10',
        'layout-surface':        '#111318',
        'layout-border':         '#252830',
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
