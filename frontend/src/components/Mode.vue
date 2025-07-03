<template>
  <div class="mode-container">
    <div class="card">
      <h2>⚙️ Modes Robot</h2>

      <!-- Zone d'erreur -->
      <div v-if="connectionError || errorMessage" class="error-banner">
        <span v-if="connectionError">⚠️ {{ errorMessage }}</span>
        <span v-else-if="errorMessage">❌ {{ errorMessage }}</span>
      </div>

      <!-- Mode Controls Grid -->
      <div class="mode-grid">
        <button
          @click="activatePolice"
          class="mode-btn police-btn"
          :class="{ active: policeActive }"
        >
          <span class="btn-icon">🚨</span>
          <span class="btn-text">{{
            policeActive ? "Stop" : "Police Mode"
          }}</span>
        </button>

        <button
          @click="toggleLineTracking"
          class="mode-btn line-btn"
          :class="{ active: lineTrackingActive }"
        >
          <span class="btn-icon">🛤️</span>
          <span class="btn-text">{{
            lineTrackingActive ? "Stop Line" : "Line Tracking"
          }}</span>
        </button>

        <button
          @click="toggleAutomaticProcessing"
          class="mode-btn auto-btn"
          :class="{ active: automaticProcessingActive }"
        >
          <span class="btn-icon">🤖</span>
          <span class="btn-text">{{
            automaticProcessingActive ? "Stop Auto" : "Automatic Processing"
          }}</span>
        </button>

        <button
          @click="toggleColorDetection"
          class="mode-btn color-btn"
          :class="{ active: colorDetectionActive }"
        >
          <span class="btn-icon">🎨</span>
          <span class="btn-text">{{
            colorDetectionActive ? "Stop Color" : "Color Detection"
          }}</span>
        </button>
      </div>

      <!-- Emergency Button -->
      <div class="emergency-section">
        <button
          class="emergency-btn"
          :class="{ active: emergencyActive }"
          @click="toggleEmergency"
        >
          <span class="emergency-icon">{{
            emergencyActive ? "🔄" : "🛑"
          }}</span>
          <span class="emergency-text">{{
            emergencyActive ? "Restart" : "Emergency Stop"
          }}</span>
        </button>
      </div>

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
const connectionError = ref(false);
const errorMessage = ref("");

onMounted(() => {
  socket.on("connect", () => {
    console.log("Connected to Socket.IO server!");
    connectionError.value = false;
    errorMessage.value = "";
  });

  socket.on("disconnect", () => {
    console.log("Disconnected from Socket.IO server.");
    connectionError.value = true;
    errorMessage.value = "Connexion perdue avec le robot";
  });

  socket.on("error", (data: { error: string }) => {
    console.error("Socket error:", data);
    errorMessage.value = data.error;
    setTimeout(() => {
      errorMessage.value = "";
    }, 5000);
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

.card {
  background-color: #1e1e1e;
  border-radius: 10px;
  padding: 2rem;
  max-width: 350px;
  margin: 0 auto;
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

/* Bannière d'erreur */
.error-banner {
  background-color: #d32f2f;
  color: white;
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: bold;
  animation: pulse-error 2s infinite;
}

@keyframes pulse-error {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
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
.btn-text {
  color: white;
}
.mode-btn {
  background-color: #1e1e1e;
  border: 2px solid var(--border-color);
}
</style>
