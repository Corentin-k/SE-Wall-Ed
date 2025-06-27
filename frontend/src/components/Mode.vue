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

    <button
      @click="toggleColorDetection"
      :class="{ active: colorDetectionActive }"
    >
      {{
        colorDetectionActive ? "Stop Color Detection" : "Start Color Detection"
      }}
    </button>

    <button
      :class="['emergency-btn', { active: emergencyActive }]"
      @click="toggleEmergency"
    >
      {{ emergencyActive ? "Restart" : "Emergency" }}
    </button>

    <!-- Section d'affichage des couleurs détectées -->
    <div
      v-if="colorDetectionActive && detectedColors.length > 0"
      class="detected-colors"
    >
      <h3>🎨 Couleurs détectées:</h3>
      <div class="color-list">
        <div
          v-for="color in detectedColors"
          :key="`${color.name}-${color.x}-${color.y}`"
          class="color-item"
        >
          <span class="color-name">{{ color.name }}</span>
          <span class="color-position"
            >({{ color.center_x }}, {{ color.center_y }})</span
          >
        </div>
      </div>
    </div>
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
const emergencyActive = ref(false);
const colorDetectionActive = ref(true); // Activé par défaut
const detectedColors = ref([]);

onMounted(() => {
  socket.on("connect", () => {
    console.log("Connected to Socket.IO server!");
  });

  socket.on("disconnect", () => {
    console.log("Disconnected from Socket.IO server.");
  });

  socket.on("emergency", (data: { active: boolean }) => {
    console.log("Emergency status:", data);
    emergencyActive.value = data.active;
  });

  // Color detection updates
  socket.on(
    "color_detection_status",
    (data: { enabled: boolean; message: string }) => {
      console.log("Color detection status:", data);
      colorDetectionActive.value = data.enabled;
    }
  );

  socket.on("detected_colors", (data: { colors: any[]; count: number }) => {
    console.log("Detected colors:", data);
    detectedColors.value = data.colors;
  });

  socket.on(
    "detected_colors_update",
    (data: { colors: any[]; timestamp: number }) => {
      detectedColors.value = data.colors;
    }
  );

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
        case "emergency":
          // En mode urgence, forcer tous les modes à false
          lineTrackingActive.value = false;
          automaticProcessingActive.value = false;
          policeActive.value = false;
          colorDetectionActive.value = false;
          break;
        case "default":
          lineTrackingActive.value = false;
          automaticProcessingActive.value = false;
          break;
      }
    }
  );

  // Récupérer l'état initial de la détection de couleur
  fetchColorDetectionStatus();
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

function toggleEmergency() {
  emergencyActive.value = !emergencyActive.value;
  socket.emit("emergency", { active: emergencyActive.value });
}

function toggleAutomaticProcessing() {
  const next = !automaticProcessingActive.value;
  socket.emit("mode", { mode: next ? "automatic_processing" : "default" });
}

function toggleLineTracking() {
  const next = !lineTrackingActive.value;
  socket.emit("mode", { mode: next ? "ligne_tracking" : "default" });
}

function toggleColorDetection() {
  const newState = !colorDetectionActive.value;
  colorDetectionActive.value = newState;
  socket.emit("toggle_color_detection", { enabled: newState });
  console.log(`Color detection ${newState ? "enabled" : "disabled"}`);
}

// Fonction pour récupérer l'état initial de la détection de couleur
async function fetchColorDetectionStatus() {
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_ROBOT_BASE_URL}/color_detection/status`
    );
    colorDetectionActive.value = response.data.enabled;
    detectedColors.value = response.data.detected_colors || [];
    console.log("Color detection status fetched:", response.data);
  } catch (error: any) {
    console.error(
      "Error fetching color detection status:",
      error.response?.data || error.message
    );
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

/* Style pour le bouton de détection de couleur */
button.active {
  background-color: #4caf50 !important; /* Vert quand actif */
  color: white !important;
}

button.active:hover {
  background-color: #45a049 !important;
}

.emergency-btn {
  background-color: #d32f2f; /* rouge vif */
  color: white; /* texte en blanc */
  border: none; /* pas de bordure */
  padding: 12px 24px; /* espacement interne généreux */
  font-size: 1.1rem; /* taille de police adaptée */
  font-weight: bold; /* effet de priorité */
  border-radius: 4px; /* coins arrondis */
  cursor: pointer; /* indique qu’on peut cliquer */
  transition: background-color 0.2s ease, transform 0.1s ease;
}

/* Au survol */
.emergency-btn:hover {
  background-color: #b71c1c;
}

/* Effet "pression" (cliquer dessus) */
.emergency-btn:active {
  transform: scale(0.98);
}

/* Quand l’état d’urgence est actif */
.emergency-btn.active {
  background-color: #ff6f00; /* orange vif pour l’action "Restart" */
}
.emergency-btn.active:hover {
  background-color: #e65a00;
}

/* Section des couleurs détectées */
.detected-colors {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #2a2a2a;
  border-radius: 8px;
  border-left: 4px solid #4caf50;
}

.detected-colors h3 {
  margin: 0 0 1rem 0;
  color: #4caf50;
  font-size: 1rem;
}

.color-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.color-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: #383838;
  border-radius: 4px;
  font-size: 0.9rem;
}

.color-name {
  font-weight: bold;
  color: #e0e0e0;
}

.color-position {
  color: #bb86fc;
  font-family: monospace;
  font-size: 0.8rem;
}
</style>
