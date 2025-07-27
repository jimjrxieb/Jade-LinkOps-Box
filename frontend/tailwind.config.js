/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        jade: {
          DEFAULT: '#3ff',
          50: '#e6ffff',
          100: '#b3ffff',
          200: '#80ffff',
          300: '#4dffff',
          400: '#1affff',
          500: '#00e6e6',
          600: '#00b3b3',
          700: '#008080',
          800: '#004d4d',
          900: '#001a1a'
        },
        backdrop: {
          light: 'rgba(255,255,255,0.05)',
          DEFAULT: 'rgba(0,0,0,0.5)',
          dark: 'rgba(0,0,0,0.8)'
        }
      },
      boxShadow: {
        glow: '0 0 10px rgba(0,255,255,0.4)',
        'glow-lg': '0 0 20px rgba(0,255,255,0.6)',
        'glow-xl': '0 0 30px rgba(0,255,255,0.8)'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-pulse': 'glow 2s ease-in-out infinite'
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(0,255,255,0.4)' },
          '50%': { boxShadow: '0 0 20px rgba(0,255,255,0.8)' }
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: [],
}
