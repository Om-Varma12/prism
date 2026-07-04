/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Core surface tokens (dark tactical palette)
        'background':            '#0A0C10',
        'surface':               '#111318',
        'surface-variant':       '#1A1D24',
        'surface-container':     '#1A1D24',
        'surface-container-low': '#141720',
        'surface-container-high':'#252830',
        'surface-container-highest': '#2E3138',
        'panel':                 '#111318',

        // Primary (blue)
        'primary':               '#3B6FE8',
        'primary-container':     '#3B6FE8',
        'primary-fixed':         '#A8C4FF',
        'inverse-primary':       '#2b5bc2',
        'on-primary':            '#FFFFFF',
        'on-primary-container':  '#FFFFFF',

        // Secondary
        'secondary':             '#6B8EFF',
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
        'DEFAULT': '6px',
        'btn':     '6px',
        'card':    '8px',
      },
    },
  },
  plugins: [],
};
