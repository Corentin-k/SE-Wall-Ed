<template>
  <div class="camera">
    <h2>Ultrasonic Sensor</h2>
    <video ref="videoElement" autoplay playsinline></video>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from "vue";

const videoElement = ref<HTMLVideoElement | null>(null);
let stream: MediaStream | null = null;

onMounted(async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (videoElement.value) {
      videoElement.value.srcObject = stream;
    }
  } catch (error) {
    console.error("Erreur d'accès à la caméra :", error);
  }
});

onBeforeUnmount(() => {
  stream?.getTracks().forEach((track) => track.stop());
});
</script>

<style scoped>
.camera {
  text-align: center;
  padding: 1rem;
  background: #1e1e1e;
  border-radius: 10px;
  max-width: 600px;
  margin: 2rem auto;
  color: white;
}

video {
  width: 100%;
  max-height: 400px;
  border: 2px solid #bb86fc;
  border-radius: 10px;
}
</style>
