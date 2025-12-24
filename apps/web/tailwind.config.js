/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  safelist: [
    // Typography
    'text-4xl', 'text-5xl', 'text-6xl', 'text-sm', 'text-lg', 'text-xl', 'text-2xl', 'text-3xl',
    'text-slate-900', 'text-slate-600', 'text-slate-500', 'text-slate-400', 'text-slate-300', 'text-white', 'text-indigo-600', 'text-gray-900', 'text-gray-600', 'text-gray-500', 'text-gray-400', 'text-amber-400', 'text-green-500', 'text-red-500',
    'font-bold', 'font-semibold', 'font-medium',
    'leading-tight', 'leading-relaxed',
    // Spacing
    'mb-6', 'mb-8', 'mb-12', 'mb-16', 'mt-8', 'mt-16', 'pt-8', 'p-4', 'p-6', 'p-8', 'px-4', 'px-6', 'px-8', 'py-4', 'py-2', 'py-3',
    // Layout
    'flex', 'grid', 'block', 'inline-flex', 'items-center', 'justify-center', 'justify-between', 'gap-4', 'gap-6', 'gap-8',
    'w-full', 'h-full', 'w-12', 'h-12', 'w-10', 'h-10',
    'max-w-7xl', 'max-w-3xl', 'max-w-xl',
    // Backgrounds
    'bg-white', 'bg-slate-50', 'bg-slate-900', 'bg-slate-800', 'bg-indigo-600', 'bg-indigo-50', 'bg-gray-100', 'bg-amber-50', 'bg-green-50', 'bg-emerald-600', 'bg-gradient-to-br', 'bg-gradient-to-r',
    // Borders
    'border', 'border-2', 'border-slate-200', 'border-slate-900', 'border-indigo-500', 'border-white',
    // Effects
    'shadow-lg', 'shadow-xl', 'shadow-2xl', 'shadow', 'shadow-md',
    'rounded-xl', 'rounded-2xl', 'rounded-3xl', 'rounded-lg', 'rounded-full', 'rounded',
    // Transitions
    'transition-all', 'transition-colors', 'transition-shadow', 'duration-200', 'duration-300',
    // Hover states
    'hover:bg-slate-100', 'hover:bg-indigo-700', 'hover:text-indigo-600', 'hover:text-white', 'hover:shadow-xl',
    // Responsive
    'sm:', 'lg:', 'xl:', 'md:',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        accent: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        highlight: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Inter', 'system-ui', 'sans-serif'],
        code: ['JetBrains Mono', 'monospace'],
        math: ['MathVerse Math', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s infinite',
        'bounce-slow': 'bounce 2s infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-pattern': "url('/images/hero-bg.svg')",
        'shimmer-gradient': 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'glow': '0 0 20px rgba(59, 130, 246, 0.3)',
        'glow-secondary': '0 0 20px rgba(16, 185, 129, 0.3)',
      },
    },
  },
  plugins: [],
};
