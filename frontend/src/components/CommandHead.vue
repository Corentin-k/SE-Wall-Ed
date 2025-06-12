<template>
  <div class="command-head" tabindex="0" @keydown="onKeyDown" @keyup="onKeyUp">
    <h2>Command Head</h2>
    <div class="button-container">
      <div class="row top-row">
        <button data-key="i" :class="{ active: headKeys.has('i') }">I</button>
      </div>
      <div class="row bottom-row">
        <button data-key="j" :class="{ active: headKeys.has('j') }">J</button>
        <button data-key="k" :class="{ active: headKeys.has('k') }">K</button>
        <button data-key="l" :class="{ active: headKeys.has('l') }">L</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";
import { io } from "socket.io-client";

const socket = io.connect('http://localhost:5000');

// Handle connection errors
socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
});

// Handle disconnection
socket.on('disconnect', () => {
  console.log('Disconnected from server');
});

const headKeys = ref(new Set<string>());

async function sendCombinedHeadCommand() {
  let pan = 0,
    tilt = 0;

  if (headKeys.value.has("l")) pan = 1;
  else if (headKeys.value.has("j")) pan = -1;

  if (headKeys.value.has("i")) tilt = 1;
  else if (headKeys.value.has("k")) tilt = -1;

  console.log("pan=", pan, "tilt=", tilt);

  const url = "http://10.3.208.73:5000/servo";
  if (pan === 0 && tilt === 0) {
    //await axios.post(`${url}/stop`);
    socket.emit('stop_head');
  } else {
    //await axios.post(`${url}/start`, { pan, tilt });
    socket.emit('move_head', { pan, tilt });
  }
}

function onKeyDown(e: KeyboardEvent) {
  const k = e.key.toLowerCase();
  if (!["i", "j", "k", "l"].includes(k)) return;
  if (!headKeys.value.has(k)) {
    headKeys.value.add(k);
    sendCombinedHeadCommand();
  }
}

function onKeyUp(e: KeyboardEvent) {
  const k = e.key.toLowerCase();
  if (headKeys.value.delete(k)) {
    sendCombinedHeadCommand();
  }
}

onMounted(() => {
  // focus to capture keys
  const el = document.querySelector(".command-head") as HTMLElement;
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
}

/* Styles inchangés */
button.active {
  outline: 3px solid var(--default-color);
  outline-offset: 2px;
}

:root {
  --default-color: #bb86fc;
}

.command-head {
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
</style>
