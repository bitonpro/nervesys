export default defineNuxtConfig({
  modules: ['@nuxt/ui'],
  ui: {
    global: true,
  },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'Sentinel - BitOn.Pro',
      htmlAttrs: {
        dir: 'rtl',
        lang: 'he'
      },
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap' }
      ]
    }
  }
})
