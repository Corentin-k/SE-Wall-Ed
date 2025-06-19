<template>
  <div class="command-motor">
    <h2>Command Motor</h2>
    <div class="button-container">
      <div class="row top-row">
        <button
          data-key="z"
          :class="{ active: motorKeys.has('z') }"
          @mousedown="() => handleButtonDown('z')"
          @mouseup="() => handleButtonUp('z')"
          @mouseleave="() => handleButtonUp('z')"
          @touchstart.prevent="() => handleButtonDown('z')"
          @touchend.prevent="() => handleButtonUp('z')"
        >
          Z
        </button>
      </div>
      <div class="row bottom-row">
        <button
          data-key="q"
          :class="{ active: motorKeys.has('q') }"
          @mousedown="() => handleButtonDown('q')"
          @mouseup="() => handleButtonUp('q')"
          @mouseleave="() => handleButtonUp('q')"
          @touchstart.prevent="() => handleButtonDown('q')"
          @touchend.prevent="() => handleButtonUp('q')"
        >
          Q
        </button>
        <button
          data-key="s"
          :class="{ active: motorKeys.has('s') }"
          @mousedown="() => handleButtonDown('s')"
          @mouseup="() => handleButtonUp('s')"
          @mouseleave="() => handleButtonUp('s')"
          @touchstart.prevent="() => handleButtonDown('s')"
          @touchend.prevent="() => handleButtonUp('s')"
        >
          S
        </button>
        <button
          data-key="d"
          :class="{ active: motorKeys.has('d') }"
          @mousedown="() => handleButtonDown('d')"
          @mouseup="() => handleButtonUp('d')"
          @mouseleave="() => handleButtonUp('d')"
          @touchstart.prevent="() => handleButtonDown('d')"
          @touchend.prevent="() => handleButtonUp('d')"
        >
          D
        </button>
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
:root {
  --default-color: #bb86fc;
}

.command-motor {
  background-color: #1e1e1e;
  border-radius: 10px;
  padding: 2rem;
  max-width: 350px;
  margin: 2rem auto;
  color: #e0e0e0;
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.row {
  display: flex;
  justify-content: center;
  gap: 1rem;
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
  min-height: 60px;
}

button:focus {
  outline: 3px solid #bb86fc;
  outline-offset: 2px;
}
button.active {
  outline: 3px solid var(--default-color);
  outline-offset: 2px;
}
</style>
