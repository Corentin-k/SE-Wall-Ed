<template>
  <div class="settings">
    <h2>Mode</h2>

    <button @click="activePolice">Police Mode</button>
    <button @click="toggleLineTracking">{{ lineTrackingActive ? 'Stop Line Tracking' : 'Start Line Tracking' }}</button>
    <button @click="updateSpeed">Light Tracking</button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref} from "vue";
import axios from "axios";
let socket: Socket;
const lineTrackingActive = ref<boolean>(false);
const ROBOT_BASE_URL = "http://10.3.208.73:5000"; 
onMounted(() => {
  // Connect to the Socket.IO server when the component is mounted
  socket = io.connect(ROBOT_BASE_URL);

  socket.on('connect', () => {
    console.log('Connected to Socket.IO server!');
  });

  socket.on('disconnect', () => {
    console.log('Disconnected from Socket.IO server.');
    lineTrackingActive.value = false; // Reset state on disconnect
  });

  // Listen for line tracking status updates from the backend
  socket.on('line_tracking_status', (data: { message: string, active: boolean }) => {
    console.log('Line tracking status:', data.message);
    lineTrackingActive.value = data.active;
  });

  socket.on('error', (data: { error: string }) => {
    console.error('Socket.IO Error:', data.error);
    alert(`Error from robot: ${data.error}`);
  });
});

onUnmounted(() => {
  // Disconnect from the Socket.IO server when the component is unmounted
  if (socket) {
    socket.disconnect();
  }
});
// on utilise un ref pour la vitesse
const speed = ref<number>(50);

async function updateSpeed() {
  try {
    // on envoie la valeur du ref directement
    const response = await axios.post("http://localhost:5000/motor/speed", {
      speed: speed.value,
    });
    console.log(response.data.message);
  } catch (error: any) {
    console.error(
      "Error updating speed:",
      error.response?.data || error.message
    );
  }
}
async function activePolice() {
  try {
    const response = await axios.post("http://10.3.208.73:5000/mode/police");
    console.log(response.data.message);
  } catch (error: any) {
    console.error(
      "Error activating police mode:",
      error.response?.data || error.message
    );
  }
}
// Function to toggle Line Tracking
async function toggleLineTracking() {
  if (lineTrackingActive.value) {
    // If active, send stop command
    socket.emit('stop_line_tracking');
  } else {
    // If inactive, send start command
    socket.emit('start_line_tracking');
  }
}
</script>

<style scoped>
:root {
  --default-color: #bb86fc;
}

.settings {
  background-color: #1e1e1e;
  border-radius: 10px;
  padding: 2rem;
  max-width: 350px;
  margin: 2rem auto;
  color: #e0e0e0;
}

input[type="number"] {
  width: 100%;
  padding: 0.5rem;
  margin: 1rem 0;
  border-radius: 4px;
  border: 1px solid #444;
  background: #2a2a2a;
  color: #e0e0e0;
}

button {
  background-color: var(--default-color);
  border: none;
  border-radius: 5px;
  padding: 0.75rem 1.25rem;
  font-weight: bold;
  color: #121212;
  cursor: pointer;
  min-width: 60px;
  margin-bottom: 1rem;
}

button:focus {
  outline: 3px solid #bb86fc;
  outline-offset: 2px;
}
</style>
