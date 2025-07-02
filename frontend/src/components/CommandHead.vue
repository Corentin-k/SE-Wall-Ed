<template>
  <div class="command-head" tabindex="0" @keydown="onKeyDown" @keyup="onKeyUp">
    <div class="card">
      <h2>Command Head</h2>

      <!-- Control Instructions -->
      <div class="instructions"></div>

      <!-- Control Layout -->
      <div class="control-container">
        <div class="direction-controls">
          <div class="control-row">
            <button
              class="control-btn up"
              data-key="i"
              :class="{ active: headKeys.has('i') }"
              @mousedown="() => handleButtonDown('i')"
              @mouseup="() => handleButtonUp('i')"
              @mouseleave="() => handleButtonUp('i')"
              @touchstart.prevent="() => handleButtonDown('i')"
              @touchend.prevent="() => handleButtonUp('i')"
            >
              <i class="icon">⬆️</i>
            </button>
          </div>

          <div class="control-row middle-row">
            <button
              class="control-btn left"
              data-key="j"
              :class="{ active: headKeys.has('j') }"
              @mousedown="() => handleButtonDown('j')"
              @mouseup="() => handleButtonUp('j')"
              @mouseleave="() => handleButtonUp('j')"
              @touchstart.prevent="() => handleButtonDown('j')"
              @touchend.prevent="() => handleButtonUp('j')"
            >
              <i class="icon">⬅️</i>
            </button>

            <div class="center-indicator">
              <div class="camera-icon">📹</div>
            </div>

            <button
              class="control-btn right"
              data-key="l"
              :class="{ active: headKeys.has('l') }"
              @mousedown="() => handleButtonDown('l')"
              @mouseup="() => handleButtonUp('l')"
              @mouseleave="() => handleButtonUp('l')"
              @touchstart.prevent="() => handleButtonDown('l')"
              @touchend.prevent="() => handleButtonUp('l')"
            >
              <i class="icon">➡️</i>
            </button>
          </div>

          <div class="control-row">
            <button
              class="control-btn down"
              data-key="k"
              :class="{ active: headKeys.has('k') }"
              @mousedown="() => handleButtonDown('k')"
              @mouseup="() => handleButtonUp('k')"
              @mouseleave="() => handleButtonUp('k')"
              @touchstart.prevent="() => handleButtonDown('k')"
              @touchend.prevent="() => handleButtonUp('k')"
            >
              <i class="icon">⬇️</i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { io } from "socket.io-client";

const socket = io.connect(import.meta.env.VITE_ROBOT_BASE_URL);

// Handle connection errors
socket.on("connect_error", (error) => {
  console.error("Connection error:", error);
});

// Handle disconnection
socket.on("disconnect", () => {
  console.log("Disconnected from server");
});

const headKeys = ref(new Set());

async function sendCombinedHeadCommand() {
  let pan = 0,
    tilt = 0;

  if (headKeys.value.has("l")) pan = -1;
  else if (headKeys.value.has("j")) pan = 1;

  if (headKeys.value.has("i")) tilt = 1;
  else if (headKeys.value.has("k")) tilt = -1;

  console.log("pan=", pan, "tilt=", tilt);

  if (pan === 0 && tilt === 0) {
    socket.emit("stop_head");
  } else {
    socket.emit("move_head", { pan, tilt });
  }
}

function onKeyDown(e) {
  const k = e.key.toLowerCase();
  if (!["i", "j", "k", "l"].includes(k)) return;
  if (!headKeys.value.has(k)) {
    headKeys.value.add(k);
    sendCombinedHeadCommand();
  }
}

function onKeyUp(e) {
  const k = e.key.toLowerCase();
  if (headKeys.value.delete(k)) {
    sendCombinedHeadCommand();
  }
}

function handleButtonDown(key) {
  if (!["i", "j", "k", "l"].includes(key) || headKeys.value.has(key)) return;
  headKeys.value.add(key);
  sendCombinedHeadCommand();
}

function handleButtonUp(key) {
  if (!headKeys.value.has(key)) return;
  headKeys.value.delete(key);
  sendCombinedHeadCommand();
}

function onHeadKeysKeyDown(e) {
  const k = e.key.toLowerCase();
  if (!["i", "j", "k", "l"].includes(k) || headKeys.has(k)) return;

  headKeys.add(k);
  sendCombinedHeadCommand();
}

function onHeadKeysKeyUp(e) {
  const k = e.key.toLowerCase();
  if (!headKeys.has(k)) return;

  headKeys.delete(k);
  sendCombinedHeadCommand();
}

onMounted(() => {
  // focus to capture keys
  const el = document.querySelector(".command-head");
  el.focus();
  document.addEventListener("keydown", onKeyDown);
  document.addEventListener("keyup", onKeyUp);
});

onBeforeUnmount(() => {
  // Clean up the event listeners
  document.removeEventListener("keydown", onKeyDown);
  document.removeEventListener("keyup", onKeyUp);
});
</script>

<style scoped>
.command-head {
  outline: none;
  max-width: 400px;
  margin: 0 auto;
}

.card {
  background-color: var(--surface-color, #1e1e1e);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.12));
}

.card h2 {
  color: var(--primary-color, #bb86fc);
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.8rem;
}

.instructions {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-secondary, rgba(255, 255, 255, 0.7));
}

.key-info {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.key {
  background-color: var(--primary-color, #bb86fc);
  color: var(--background-color, #121212);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.control-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.direction-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 240px;
  margin: 0 auto;
}

.control-row {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.middle-row {
  align-items: center;
}

.control-btn {
  background-color: var(--surface-color, #2a2a2a);
  border: 2px solid var(--border-color, rgba(255, 255, 255, 0.12));
  color: var(--text-primary, #ffffff);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 70px;
  min-height: 70px;
  font-size: 0.9rem;
  font-weight: 500;
  user-select: none;
}

.control-btn:hover {
  background-color: var(--primary-color, #bb86fc);
  color: var(--background-color, #121212);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(187, 134, 252, 0.3);
}

.control-btn:active,
.control-btn.active {
  background-color: var(--primary-color, #bb86fc);
  color: var(--background-color, #121212);
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(187, 134, 252, 0.4);
}

.icon {
  font-size: 1.5rem;
}

.label {
  font-size: 0.8rem;
  text-align: center;
}

.center-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 70px;
  min-height: 70px;
}

.camera-icon {
  font-size: 2rem;
  color: var(--primary-color, #bb86fc);
}

.stop-controls {
  display: flex;
  justify-content: center;
}

.stop-btn {
  background-color: var(--error-color, #cf6679);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(207, 102, 121, 0.3);
}

.stop-btn:hover {
  background-color: #e74c3c;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(231, 76, 60, 0.4);
}

.stop-btn:active {
  transform: translateY(0);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .card {
    padding: 1.5rem;
    margin: 0 1rem;
  }

  .card h2 {
    font-size: 1.5rem;
  }

  .control-btn {
    min-width: 60px;
    min-height: 60px;
    padding: 0.75rem;
  }

  .icon {
    font-size: 1.3rem;
  }

  .label {
    font-size: 0.7rem;
  }

  .camera-icon {
    font-size: 1.5rem;
  }

  .stop-btn {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .card {
    padding: 1rem;
  }

  .control-btn {
    min-width: 50px;
    min-height: 50px;
    padding: 0.5rem;
  }

  .icon {
    font-size: 1.1rem;
  }

  .label {
    font-size: 0.6rem;
  }

  .key-info {
    flex-direction: column;
    gap: 0.5rem;
  }

  .center-indicator {
    min-width: 50px;
    min-height: 50px;
  }

  .camera-icon {
    font-size: 1.2rem;
  }
}
</style>
