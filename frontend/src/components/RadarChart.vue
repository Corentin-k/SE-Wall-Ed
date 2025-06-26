<template>
  <div class="radar-container">
    <canvas ref="canvas" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";

const canvas = ref(null);
const width = 420;
const height = 230;
const radius = 180;
let angle = 0;
let direction = 1;
let animationFrame;


const angles = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180];
const distances = [120, 110, 95, 85, 75, 65, 60, 70, 80, 100, 130, 160, 180];

// Fonction pour convertir (angle, distance) → (x, y) canvas
function polarToCartesian(angleDeg, distance) {
  const rad = (angleDeg * Math.PI) / 180;
  const x = width / 2 + distance * Math.cos(rad);
  const y = height - distance * Math.sin(rad);
  return { x, y };
}

function drawScan(ctx) {
  ctx.clearRect(0, 0, width, height);

  // Demi-cercle de fond
  ctx.beginPath();
  ctx.arc(width / 2, height, radius, Math.PI, 0, false);
  ctx.fillStyle = "#001f3f";
  ctx.fill();

  // Graduation
  ctx.strokeStyle = "#004d66";
  ctx.lineWidth = 1;
  for (let a = 0; a <= 180; a += 30) {
    const rad = (a * Math.PI) / 180;
    const x = width / 2 + radius * Math.cos(rad);
    const y = height - radius * Math.sin(rad);
    ctx.beginPath();
    ctx.moveTo(width / 2, height);
    ctx.lineTo(x, y);
    ctx.stroke();
  }

  // Données (points rouges)
  ctx.fillStyle = "red";
  angles.forEach((a, i) => {
    const d = distances[i];
    const { x, y } = polarToCartesian(a, d);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, 2 * Math.PI);
    ctx.fill();
  });

  // Rayon du scan animé
  const rad = (angle * Math.PI) / 180;
  const x = width / 2 + radius * Math.cos(rad);
  const y = height - radius * Math.sin(rad);
  ctx.beginPath();
  ctx.moveTo(width / 2, height);
  ctx.lineTo(x, y);
  ctx.strokeStyle = "lime";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Mise à jour de l'angle
  angle += direction * 2;
  if (angle >= 180 || angle <= 0) direction *= -1;

  //   animationFrame = requestAnimationFrame(() => drawScan(ctx));
  // Graduation (traits + texte)
  ctx.strokeStyle = "#004d66";
  ctx.lineWidth = 1;
  ctx.font = "12px Arial";
  ctx.fillStyle = "#00bfff"; // Couleur du texte

  for (let a = 0; a <= 180; a += 30) {
    const rad = (a * Math.PI) / 180;
    const x = width / 2 + radius * Math.cos(rad);
    const y = height - radius * Math.sin(rad);

    // Trait
    ctx.beginPath();
    ctx.moveTo(width / 2, height);
    ctx.lineTo(x, y);
    ctx.stroke();

    // Position du texte (légèrement à l’extérieur du cercle)
    const labelRadius = radius + 15;
    const lx = width / 2 + labelRadius * Math.cos(rad);
    const ly = height - labelRadius * Math.sin(rad);

    ctx.fillText(`${a}°`, lx - 10, ly); // -10 pour centrer le texte
  }
}

onMounted(() => {
  const ctx = canvas.value.getContext("2d");
  drawScan(ctx);
});

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrame);
});
</script>

<style scoped>
.radar-container {
  text-align: center;
  padding: 1rem;
  background: #1e1e1e;
  border-radius: 10px;
  max-width: 640px;
  margin: 2rem auto;
  color: white;
}
.radar-container {
  width: 100%;
  border: 2px solid #bb86fc;
  border-radius: 10px;
}
</style>
