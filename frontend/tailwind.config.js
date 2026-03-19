/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e8f0fa',
          100: '#c5d7f2',
          200: '#9ebbe9',
          300: '#769edf',
          400: '#5889d8',
          500: '#3a74d1',
          600: '#2a5fbb',
          700: '#1d4a9f',
          800: '#133784',
          900: '#0F4C81',
        },
        teal: {
          400: '#26c6b5',
          500: '#00BFA5',
          600: '#00a98f',
        },
        danger: '#E53935',
        warning: '#FB8C00',
        success: '#43A047',
        surface: '#FFFFFF',
        bg: '#F8FAFC',
      },
      fontFamily: {
        heading: ['Sora', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        card: '12px',
        input: '8px',
        badge: '999px',
      },
      boxShadow: {
        card: '0 4px 24px rgba(15, 76, 129, 0.08)',
        'card-hover': '0 8px 40px rgba(15, 76, 129, 0.15)',
        glow: '0 0 20px rgba(0, 191, 165, 0.25)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
