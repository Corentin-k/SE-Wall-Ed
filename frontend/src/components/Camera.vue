<template>
  <div class="camera">
    <h2>Camera</h2>
    <!-- <img src="http://10.3.208.73:5000/camera" alt="Video Stream" /> -->
    <canvas ref="canva" width="640" height="480"></canvas>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, useTemplateRef } from "vue";

const videoElement = ref<HTMLVideoElement | null>(null);
let stream: MediaStream | null = null;
let canvaElement = useTemplateRef("canva");

// let image = new Image();
// image.crossOrigin = "Anonymous";

// image.onload = () => {
//   var context2d = canvaElement.value.getContext("2d");
//   context2d.drawImage(image, 0, 0, 640, 480);
//   requestAnimationFrame(fetchImage)
// };

// const fetchImage = function() {
//   image.src = "http://10.3.208.73:5000/camera?rand=" + Math.random();
  
// }

// onMounted(async () => {
//   try {
//     stream = await navigator.mediaDevices.getUserMedia({ video: true });
//     if (videoElement.value) {
//       videoElement.value.srcObject = stream;
//     }
//   } catch (error) {
//     console.error("Erreur d'accès à la caméra :", error);
//   }

//   if(canvaElement.value != null){
//     requestAnimationFrame(fetchImage)
//   }
//   else{
//    console.error("Canvas element is not defined");
//   }
  
// });

// onBeforeUnmount(() => {
//   stream?.getTracks().forEach((track) => track.stop());
// });

import { io } from "socket.io-client";

const socket = io.connect(import.meta.env.VITE_ROBOT_BASE_URL);
onMounted(() => {
  var context2d = canvaElement.value.getContext("2d");

  socket.of("/video_stream").on("video", function(frame){
    context2d.putImageData(frame, 0, 0);
  })
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

img {
  width: 100%;
  max-height: 400px;
  border: 2px solid #bb86fc;
  border-radius: 10px;
}

canva {
  border: 2px solid #bb86fc;
  border-radius: 10px;
}
</style>
