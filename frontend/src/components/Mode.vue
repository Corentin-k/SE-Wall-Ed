<template>
  <div class="settings">
    <h2>Mode</h2>

    <button @click="activatePolice">Police Mode</button>
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

const lineTrackingActive = ref(false);
const automaticProcessingActive = ref(false);
const socket: Socket = io(import.meta.env.VITE_ROBOT_BASE_URL);

onMounted(() => {
  socket.on("connect", () => {
    console.log("Connected to Socket.IO server!");
  });

  socket.on("disconnect", () => {
    console.log("Disconnected from Socket.IO server.");
    lineTrackingActive.value = false;
  });

  // Line tracking updates
  socket.on(
    "line_tracking_status",
    (data: { message: string; active: boolean }) => {
      console.log("Line tracking status:", data.message);
      lineTrackingActive.value = data.active;
    }
  );
});

onUnmounted(() => {
  socket.disconnect();
});

async function toggleAutomaticProcessing() {
  try {
    const mode = automaticProcessingActive.value ? "stop" : "start";
    if (mode === "stop") {
      automaticProcessingActive.value = false;
    } else {
      automaticProcessingActive.value = true;
    }
    const res = await axios.post(
      `${import.meta.env.VITE_ROBOT_BASE_URL}/mode/automatic_processing`,
      { mode }
    );
    console.log(res.data.message);
  } catch (error: any) {
    console.error(error.response?.data || error.message);
  }
}

async function activatePolice() {
  try {
    const res = await axios.post(
      `${import.meta.env.VITE_ROBOT_BASE_URL}/mode/police`
    );
    console.log(res.data.message);
  } catch (error: any) {
    console.error(
      "Error activating police mode:",
      error.response?.data || error.message
    );
  }
}

async function toggleLineTracking() {
  if (lineTrackingActive.value) {
    socket.emit("stop_line_tracking");
  } else {
    socket.emit("start_line_tracking");
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
