<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-semibold">מכשירים מחוברים</h2>
        <p class="text-gray-500 mt-1">ניהול ציי מכשירי אנדרואיד באמצעות MCP</p>
      </div>
      <UButton color="brand" icon="i-heroicons-plus">הוסף מכשיר</UButton>
    </div>

    <!-- Devices List -->
    <UCard>
      <UTable :rows="devices" :columns="columns">
        <template #status-data="{ row }">
          <UBadge :color="row.status === 'online' ? 'green' : 'gray'" variant="subtle">
            {{ row.status }}
          </UBadge>
        </template>
        <template #actions-data="{ row }">
          <UButton color="gray" variant="ghost" icon="i-heroicons-ellipsis-horizontal" />
        </template>
      </UTable>
    </UCard>

    <!-- OpenClaw Integration -->
    <div class="mt-8">
      <h3 class="text-lg font-medium mb-4">אינטגרציית OpenClaw</h3>
      <UCard>
        <div class="space-y-4 max-w-lg">
          <UFormGroup label="Endpoint URL">
            <UInput v-model="openClawConfig.endpoint" placeholder="https://..." />
          </UFormGroup>
          <UFormGroup label="ערוץ העברה">
            <USelect v-model="openClawConfig.deliveryChannel" :options="['WhatsApp', 'Telegram']" />
          </UFormGroup>
          <UFormGroup label="נמען">
            <UInput v-model="openClawConfig.deliverTo" placeholder="+972..." />
          </UFormGroup>
          <div class="pt-4 flex justify-end">
            <UButton color="brand" @click="saveConfig">שמור הגדרות</UButton>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import { useMcpClient } from '~/composables/useMcpClient'
import { onMounted } from 'vue'

const { devices, fetchDevices, openClawConfig, saveOpenClawConfig } = useMcpClient()

const columns = [
  { key: 'name', label: 'מכשיר' },
  { key: 'id', label: 'מזהה' },
  { key: 'status', label: 'סטטוס' },
  { key: 'lastSeen', label: 'נראה לאחרונה' },
  { key: 'actions' }
]

onMounted(() => {
  fetchDevices()
})

const saveConfig = () => {
  saveOpenClawConfig(openClawConfig.value)
}
</script>
