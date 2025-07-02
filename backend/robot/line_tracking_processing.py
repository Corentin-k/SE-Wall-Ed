<template>
  <div class="camera-container">
    <div class="camera-header">
      <h2>📹 Caméra Robot</h2>
      <div class="camera-status">
        <span class="status-dot" :class="{ connected: isConnected }"></span>
        <span class="status-text">{{
          isConnected ? "Connecté" : "Déconnecté"
        }}</span>
      </div>
    </div>

    <div class="camera-wrapper">
      <div class="video-container">
        <img
          :src="streamUrl"
          alt="Flux vidéo du robot"
          @load="handleImageLoad"
          @error="handleImageError"
          class="video-stream"
        />
        <div v-if="!isConnected" class="connection-overlay">
          <div class="connection-message"></div>
        </div>
      </div>

      <div class="camera-controls">
        <button @click="toggleFullscreen" class="control-btn">
          🔍 Plein écran
        </button>
        <button @click="takeScreenshot" class="control-btn">📸 Capture</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const streamUrl = import.meta.env.VITE_ROBOT_BASE_URL + "/camera";
const isConnected = ref(false);

const handleImageLoad = () => {
  isConnected.value = true;
};

const handleImageError = () => {
  isConnected.value = false;
};

const toggleFullscreen = () => {
  const videoElement = document.querySelector(
    ".video-stream"
  ) as HTMLImageElement;
  if (videoElement) {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      videoElement.requestFullscreen();
    }
  }
};

const takeScreenshot = () => {
  const videoElement = document.querySelector(
    ".video-stream"
  ) as HTMLImageElement;
  if (videoElement) {
    // Créer un canvas pour capturer l'image
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    canvas.width = videoElement.naturalWidth;
    canvas.height = videoElement.naturalHeight;

    if (ctx) {
      ctx.drawImage(videoElement, 0, 0);

      // Télécharger l'image
      const link = document.createElement("a");
      link.download = `robot-screenshot-${new Date().toISOString()}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  }
};
</script>

<style scoped>
.camera-container {
  background-color: var(--surface-color, #1e1e1e);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.12));
  max-width: 100%;
  margin: 0 auto;
}

.camera-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.camera-header h2 {
  color: var(--primary-color, #bb86fc);
  font-size: 1.5rem;
  margin: 0;
}

.camera-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary, rgba(255, 255, 255, 0.7));
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: var(--error-color, #cf6679);
  transition: background-color 0.3s ease;
}

.status-dot.connected {
  background-color: var(--secondary-color, #03dac6);
}

.camera-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.video-container {
  position: relative;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  background-color: var(--background-color, #121212);
  border: 2px solid var(--primary-color, #bb86fc);
}

.video-stream {
  width: 100%;
  height: auto;
  display: block;
  max-width: 100%;
  object-fit: contain;
}

.connection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(18, 18, 18, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary, #ffffff);
}

.connection-message {
  text-align: center;
  padding: 2rem;
}

.connection-message .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.connection-message p {
  font-size: 1.1rem;
  margin: 0;
}

.camera-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.control-btn {
  background-color: var(--surface-color, #2a2a2a);
  color: var(--text-primary, #ffffff);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.12));
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-btn:hover {
  background-color: var(--primary-color, #bb86fc);
  color: var(--background-color, #121212);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(187, 134, 252, 0.3);
}

.control-btn:active {
  transform: translateY(0);
}

/* Responsive Design */
@media (max-width: 768px) {
  .camera-container {
    padding: 1rem;
  }

  .camera-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .camera-header h2 {
    font-size: 1.3rem;
  }

  .camera-status {
    font-size: 0.8rem;
  }

  .control-btn {
    padding: 0.6rem 1.2rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .camera-container {
    padding: 0.75rem;
  }

  .camera-header h2 {
    font-size: 1.2rem;
  }

  .camera-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .control-btn {
    padding: 0.75rem;
    justify-content: center;
  }

  .connection-message {
    padding: 1rem;
  }

  .connection-message .icon {
    font-size: 2rem;
  }

  .connection-message p {
    font-size: 1rem;
  }
}

/* Fullscreen styles */
.video-stream:fullscreen {
  width: 100vw;
  height: 100vh;
  object-fit: contain;
}
</style>
