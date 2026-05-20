<template>
  <div dir="rtl" class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans">
    <header class="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <UIcon name="i-heroicons-shield-check" class="text-brand-500 w-8 h-8" />
        <h1 class="text-xl font-bold font-heebo tracking-tight">Sentinel MCP</h1>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500">BitOn.Pro Device Management</span>
        <UButton color="gray" variant="ghost" icon="i-heroicons-moon" @click="toggleColorMode" />
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup>
const colorMode = useColorMode()
const toggleColorMode = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>
