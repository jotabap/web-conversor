/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
  ],
  theme: {
    extend: {
      // Aquí puedes agregar personalizaciones
      colors: {
        // Ejemplo: agregar colores personalizados
        // 'custom-blue': '#1e40af',
      },
      fontFamily: {
        // Ejemplo: agregar fuentes personalizadas
        // 'custom': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
