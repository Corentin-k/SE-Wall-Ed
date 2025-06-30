<template>
  <div class="radar-container">
    <h3>🎯 Radar Scanner</h3>
    <div class="radar-controls">
      <button
        @click="triggerRadarScan"
        class="scan-button"
        :disabled="scanning"
      >
        {{ scanning ? "⏳ Scan en cours..." : "🔄 Lancer Scan" }}
      </button>
      <div class="radar-info">
        <span v-if="lastUpdate"
          >Dernière mise à jour: {{ formatTime(lastUpdate) }}</span
        >
        <span v-if="pointCount > 0">{{ pointCount }} points détectés</span>
      </div>
    </div>
    <canvas ref="canvas" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { io } from "socket.io-client";

const canvas = ref(null);
const width = 420;
const height = 230;
const radius = 180;
let angle = 0;
let direction = 1;
let animationFrame;

// Socket connection
const socket = io(import.meta.env.VITE_ROBOT_BASE_URL);

// État du composant
const angles = ref([0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]);
const distances = ref([
  120, 110, 95, 85, 75, 65, 60, 70, 80, 100, 130, 160, 180,
]);
const lastUpdate = ref(null);
const scanning = ref(false);
const pointCount = ref(0);

// Fonctions utilitaires
function polarToCartesian(angleDeg, distance) {
  const rad = (angleDeg * Math.PI) / 180;
  const x = width / 2 + distance * Math.cos(rad);
  const y = height - distance * Math.sin(rad);
  return { x, y };
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString();
}

function drawScan(ctx) {
  ctx.clearRect(0, 0, width, height);

  // Demi-cercle de fond
  ctx.beginPath();
  ctx.arc(width / 2, height, radius, Math.PI, 0, false);
  ctx.fillStyle = "#001f3f";
  ctx.fill();

  // Cercles de distance
  ctx.strokeStyle = "#003d66";
  ctx.lineWidth = 1;
  for (let r = 60; r <= radius; r += 60) {
    ctx.beginPath();
    ctx.arc(width / 2, height, r, Math.PI, 0, false);
    ctx.stroke();

    // Labels de distance
    ctx.fillStyle = "#004d66";
    ctx.font = "10px Arial";
    ctx.fillText(`${Math.round(r / 1.5)}cm`, width / 2 + r - 15, height - 5);
  }

  // Graduation (traits + texte)
  ctx.strokeStyle = "#004d66";
  ctx.lineWidth = 1;
  ctx.font = "12px Arial";
  ctx.fillStyle = "#00bfff";

  for (let a = 0; a <= 180; a += 30) {
    const rad = (a * Math.PI) / 180;
    const x = width / 2 + radius * Math.cos(rad);
    const y = height - radius * Math.sin(rad);

    // Trait
    ctx.beginPath();
    ctx.moveTo(width / 2, height);
    ctx.lineTo(x, y);
    ctx.stroke();

    // Texte d'angle
    const labelRadius = radius + 15;
    const lx = width / 2 + labelRadius * Math.cos(rad);
    const ly = height - labelRadius * Math.sin(rad);
    ctx.fillText(`${a}°`, lx - 10, ly);
  }

  // Données radar (points et zones)
  if (angles.value.length > 0) {
    // Dessiner les zones d'obstacles
    ctx.beginPath();
    ctx.moveTo(width / 2, height);

    angles.value.forEach((a, i) => {
      if (i < distances.value.length) {
        const d = Math.min(distances.value[i] * 1.5, radius);
        const { x, y } = polarToCartesian(a, d);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    });

    ctx.strokeStyle = "rgba(255, 0, 0, 0.6)";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Points individuels
    ctx.fillStyle = "#ff4444";
    angles.value.forEach((a, i) => {
      if (i < distances.value.length) {
        const d = Math.min(distances.value[i] * 1.5, radius);
        const { x, y } = polarToCartesian(a, d);

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();

        // Afficher distance pour obstacles proches
        if (distances.value[i] < 50) {
          ctx.fillStyle = "#ffff00";
          ctx.font = "10px Arial";
          ctx.fillText(`${Math.round(distances.value[i])}`, x + 6, y - 6);
          ctx.fillStyle = "#ff4444";
        }
      }
    });
  }

  // Rayon du scan animé
  const rad = (angle * Math.PI) / 180;
  const x = width / 2 + radius * Math.cos(rad);
  const y = height - radius * Math.sin(rad);

  // Effet de balayage
  const gradient = ctx.createLinearGradient(width / 2, height, x, y);
  gradient.addColorStop(0, "rgba(0, 255, 0, 0.8)");
  gradient.addColorStop(1, "rgba(0, 255, 0, 0.1)");

  ctx.beginPath();
  ctx.moveTo(width / 2, height);
  ctx.lineTo(x, y);
  ctx.strokeStyle = gradient;
  ctx.lineWidth = 3;
  ctx.stroke();

  // Point du scanner
  ctx.beginPath();
  ctx.arc(x, y, 6, 0, 2 * Math.PI);
  ctx.fillStyle = "#00ff00";
  ctx.fill();

  // Animation
  angle += direction * 1.5;
  if (angle >= 180 || angle <= 0) direction *= -1;
}

function startAnimation() {
  const ctx = canvas.value?.getContext("2d");
  if (ctx) {
    drawScan(ctx);
    animationFrame = requestAnimationFrame(startAnimation);
  }
}

function triggerRadarScan() {
  if (scanning.value) return;

  console.log("🎯 Démarrage du scan radar...");
  scanning.value = true;

  socket.emit("start_radar_scan", {
    min_angle: 0,
    max_angle: 180,
    step: 10,
  });

  // Timeout de sécurité
  setTimeout(() => {
    if (scanning.value) {
      scanning.value = false;
      console.warn("Timeout du scan radar");
    }
  }, 30000); // 30 secondes max
}

onMounted(() => {
  console.log("🎯 RadarChart monté");

  // WebSocket events
  socket.on("connect", () => {
    console.log("✅ Radar: Connected to robot");
  });

  socket.on("radar_scan_result", (data) => {
    console.log("📡 Radar scan received:", data);
    angles.value = data.angles;
    distances.value = data.distances;
    lastUpdate.value = Date.now();
    pointCount.value = data.angles.length;
    scanning.value = false;
  });

  socket.on("error", (error) => {
    console.error("❌ Radar error:", error);
    scanning.value = false;
  });

  socket.on("disconnect", () => {
    console.log("⚠️ Radar: Disconnected from robot");
    scanning.value = false;
  });

  // Démarrer l'animation
  startAnimation();
});

onBeforeUnmount(() => {
  console.log("🎯 RadarChart démonté");
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
  socket.disconnect();
});
</script>

<style scoped>
.radar-container {
  text-align: center;
  padding: 1.5rem;
  background: #1e1e1e;
  border-radius: 15px;
  max-width: 500px;
  margin: 2rem auto;
  color: white;
  border: 2px solid #bb86fc;
  box-shadow: 0 4px 15px rgba(187, 134, 252, 0.3);
}

.radar-container h3 {
  margin: 0 0 1rem 0;
  color: #bb86fc;
  font-size: 1.3rem;
}

.radar-controls {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.scan-button {
  background: linear-gradient(45deg, #bb86fc, #03dac6);
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: bold;
  color: #121212;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.scan-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(187, 134, 252, 0.4);
}

.scan-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.radar-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #03dac6;
  opacity: 0.8;
}

canvas {
  border: 1px solid #333;
  border-radius: 10px;
  background: #0a0a0a;
}

@media (max-width: 480px) {
  .radar-container {
    padding: 1rem;
    margin: 1rem;
  }

  .radar-info {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>
