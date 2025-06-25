<template>
  <div class="settings">
    <h2>Mode</h2>

    <button @click="activatePolice">
      {{ policeActive ? "Arrêter Police Mode" : "Démarrer Police Mode" }}
    </button>

    <button @click="toggleLineTracking">
      {{ lineTrackingActive ? "Stop Line Tracking" : "Start Line Tracking" }}
    </button>
    <button @click="toggleAutomaticProcessing">
      {{
        automaticProcessingActive
          ? "Stop Automatic Processing"
          : "Start Automatic Processing"
      }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { io, Socket } from "socket.io-client";
import axios from "axios";

const socket: Socket = io(import.meta.env.VITE_ROBOT_BASE_URL);

const policeActive = ref(false);
const lineTrackingActive = ref(false);
const automaticProcessingActive = ref(false);

onMounted(() => {
  socket.on("connect", () => {
    console.log("Connected to Socket.IO server!");
  });

  socket.on("disconnect", () => {
    console.log("Disconnected from Socket.IO server.");
  });

  // Line tracking updates
  socket.on(
    "mode_status",
    (data: { mode: string; active: boolean; message: string }) => {
      console.log("mode_status:", data);
      // mettre à jour les flags en fonction du mode retourné
      switch (data.mode) {
        case "ligne_tracking":
          lineTrackingActive.value = data.active;
          break;
        case "automatic_processing":
          automaticProcessingActive.value = data.active;
          break;
      }
    }
  );
});

onUnmounted(() => {
  socket.disconnect();
});

async function activatePolice() {
  try {
    const res = await axios.post(
      `${import.meta.env.VITE_ROBOT_BASE_URL}/mode/police`
    );
    policeActive.value = !policeActive.value;
    console.log(res.data.message);
  } catch (error: any) {
    console.error(
      "Error activating police mode:",
      error.response?.data || error.message
    );
  }
}

function toggleAutomaticProcessing() {
  const next = !automaticProcessingActive.value;
  socket.emit("mode", { mode: next ? "RadarController" : "default" });
}

function toggleLineTracking() {
  const next = !lineTrackingActive.value;
  socket.emit("mode", { mode: next ? "ligne_tracking" : "default" });
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
