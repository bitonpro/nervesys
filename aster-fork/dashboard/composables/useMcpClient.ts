import { ref } from 'vue'

export const useMcpClient = () => {
  const isConnected = ref(false)
  const devices = ref([])
  const error = ref(null)

  const connect = async (url) => {
    try {
      // Setup WebSocket connection to Sentinel MCP Server
      console.log(`Connecting to ${url}...`)
      isConnected.value = true
    } catch (e) {
      error.value = e.message
      isConnected.value = false
    }
  }

  const fetchDevices = async () => {
    // Dummy fetch devices
    devices.value = [
      { id: '1', name: 'nubia NP05J', status: 'online', lastSeen: 'just now' }
    ]
  }

  return {
    isConnected,
    devices,
    error,
    connect,
    fetchDevices
  }
}
