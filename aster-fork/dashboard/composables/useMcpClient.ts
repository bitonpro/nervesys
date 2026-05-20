import { ref } from 'vue'

export const useMcpClient = () => {
  const isConnected = ref(false)
  const devices = ref([])
  const error = ref(null)

  // OpenClaw Integration
  const openClawConfig = ref({
    enabled: false,
    endpoint: '',
    authToken: '',
    deliveryChannel: 'WhatsApp',
    deliverTo: '',
    events: {
      notifications: true,
      sms: true,
      connected: true,
      disconnected: true
    }
  })

  const connect = async (url) => {
    try {
      console.log(`Connecting to ${url}...`)
      isConnected.value = true
    } catch (e) {
      error.value = e.message
      isConnected.value = false
    }
  }

  const fetchDevices = async () => {
    devices.value = [
      { id: '1', name: 'nubia NP05J', status: 'online', lastSeen: 'just now' }
    ]
  }

  const saveOpenClawConfig = async (config) => {
    console.log('Saving OpenClaw configuration to MCP...', config)
    openClawConfig.value = config
  }

  return {
    isConnected,
    devices,
    error,
    openClawConfig,
    connect,
    fetchDevices,
    saveOpenClawConfig
  }
}
