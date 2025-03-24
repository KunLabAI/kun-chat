/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx,css}",
  ],
  darkMode: 'class', // 启用 class 策略的深色模式
  theme: {
    extend: {
      height: {
        screen: '100%' // 这里将 h-screen 的值从 100vh 改为 100%
      },
    },
  },
}
