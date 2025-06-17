<template>
  <div class="camera">
    <h2>Camera</h2>
    <!-- Le navigateur gère nativement le MJPEG -->
    <img :src="streamUrl" alt="Video Stream" />
  </div>
</template>

<script setup lang="ts">
const streamUrl = 'http://10.3.208.73:5000/camera';
</script>

<style scoped>
.camera {
  text-align: center;
  padding: 1rem;
  background: #1e1e1e;
  border-radius: 10px;
  max-width: 640px;
  margin: 2rem auto;
  color: white;
}
img {
  width: 100%;
  border: 2px solid #bb86fc;
  border-radius: 10px;
}
</style>
