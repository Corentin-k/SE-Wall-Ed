<template>
  <div class="command-head" tabindex="0" @keydown="onKeyDown" @keyup="onKeyUp">
    <div class="card">
      <h2>Command Motor</h2>

      <!-- Control Instructions -->
      <div class="instructions"></div>

      <!-- Control Layout -->
      <div class="control-container">
        <div class="direction-controls">
          <div class="control-row">
            <button
              class="control-btn up"
              data-key="z"
              :class="{ active: motorKeys.has('z') }"
              @mousedown="() => handleButtonDown('z')"
              @mouseup="() => handleButtonUp('z')"
              @mouseleave="() => handleButtonUp('z')"
              @touchstart.prevent="() => handleButtonDown('z')"
              @touchend.prevent="() => handleButtonUp('z')"
            >
              <i class="icon">⬆️ </i>
            </button>
          </div>

          <div class="control-row middle-row">
            <button
              class="control-btn left"
              data-key="q"
              :class="{ active: motorKeys.has('q') }"
              @mousedown="() => handleButtonDown('q')"
              @mouseup="() => handleButtonUp('q')"
              @mouseleave="() => handleButtonUp('q')"
              @touchstart.prevent="() => handleButtonDown('q')"
              @touchend.prevent="() => handleButtonUp('q')"
            >
              <i class="icon">⬅️</i>
            </button>

            <div class="center-indicator">
              <div class="camera-icon">🏍️</div>
            </div>

            <button
              class="control-btn right"
              data-key="d"
              :class="{ active: motorKeys.has('d') }"
              @mousedown="() => handleButtonDown('d')"
              @mouseup="() => handleButtonUp('d')"
              @mouseleave="() => handleButtonUp('d')"
              @touchstart.prevent="() => handleButtonDown('d')"
              @touchend.prevent="() => handleButtonUp('d')"
            >
              <i class="icon">➡️</i>
            </button>
          </div>

          <div class="control-row">
            <button
              class="control-btn down"
              data-key="s"
              :class="{ active: motorKeys.has('s') }"
              @mousedown="() => handleButtonDown('s')"
              @mouseup="() => handleButtonUp('s')"
              @mouseleave="() => handleButtonUp('s')"
              @touchstart.prevent="() => handleButtonDown('s')"
              @touchend.prevent="() => handleButtonUp('s')"
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
import { reactive, onMounted, onBeforeUnmount } from "vue";
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

// Set réactif pour suivre les touches moteur enfoncées
const motorKeys = reactive(new Set());

function sendMotor() {
  if (motorKeys.has("z")) {
    socket.emit("motor_move", { speed: 100 });
  } else if (motorKeys.has("s")) {
    socket.emit("motor_move", { speed: -100 });
  } else {
    socket.emit("motor_move", { speed: 0 });
  }

  if (motorKeys.has("d")) {
    socket.emit("turn_wheel", { direction: "right" });
  } else if (motorKeys.has("q")) {
    socket.emit("turn_wheel", { direction: "left" });
  } else {
    socket.emit("turn_wheel", { direction: "forward" });
  }
}
function handleButtonDown(key) {
  if (!["z", "q", "s", "d"].includes(key) || motorKeys.has(key)) return;
  motorKeys.add(key);
  sendMotor();
}

function handleButtonUp(key) {
  if (!motorKeys.has(key)) return;
  motorKeys.delete(key);
  sendMotor();
}

function onMotorKeyDown(e) {
  const k = e.key.toLowerCase();
  if (!["z", "q", "s", "d"].includes(k) || motorKeys.has(k)) return;

  motorKeys.add(k);
  sendMotor();
}

function onMotorKeyUp(e) {
  const k = e.key.toLowerCase();
  if (!motorKeys.has(k)) return;

  motorKeys.delete(k);
  sendMotor();
}

onMounted(() => {
  window.addEventListener("keydown", onMotorKeyDown);
  window.addEventListener("keyup", onMotorKeyUp);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onMotorKeyDown);
  window.removeEventListener("keyup", onMotorKeyUp);
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
