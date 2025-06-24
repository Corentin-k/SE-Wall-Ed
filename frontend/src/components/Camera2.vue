<template>
  <div class="camera">
    <h2>Camera</h2>
    <!-- <img src="http://10.3.208.73:5000/camera" alt="Video Stream" /> -->
    <canvas ref="canva" width="640" height="480"></canvas>
    <!-- <img ref="img"/> -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, useTemplateRef } from "vue";

const videoElement = ref<HTMLVideoElement | null>(null);
let stream: MediaStream | null = null;
let canvas = useTemplateRef("canva");
const img = new Image();
// let imgElement = useTemplateRef("img");

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
let isRendering = false;
let latestFrame: string | null = null;
let image_count = 0;
let start_time = 0;
onMounted(() => {
  const socket = io.connect(import.meta.env.VITE_ROBOT_BASE_URL+"/video_stream");
  var context2d = canvas.value.getContext("2d");

  socket.on("video", (frame: string) => {
    // Save the latest frame but don't decode immediately
    latestFrame = frame;

    // If we're not rendering anything, start decoding
    if (!isRendering) {
      drawLatestFrame();
    }
  });

  const drawLatestFrame = () => {
    if (!latestFrame) return;

    isRendering = true;
    img.src = latestFrame;
    latestFrame = null;

    img.onload = () => {
      if (canvas.value) {
        context2d.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
      }

      isRendering = false;

      // If a newer frame came in while we were rendering, draw it
      if (latestFrame) {
        drawLatestFrame();
      }
    };
  };
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

canvas {
  border: 2px solid #bb86fc;
  border-radius: 10px;
}
</style>
