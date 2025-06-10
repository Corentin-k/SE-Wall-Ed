<template>
  <div class="command-head">
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
import { reactive, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";

const headKeys = reactive(new Set<string>());

async function sendHead(direction: string) {
  await axios.post("/head", { direction });
}

function onHeadKeyDown(e: KeyboardEvent) {
  const k = e.key.toLowerCase();
  if (!["i", "j", "k", "l"].includes(k) || headKeys.has(k)) return;

  headKeys.add(k);
  const dirMap: Record<string, string> = {
    i: "up",
    j: "left",
    k: "down",
    l: "right",
  };
  sendHead(dirMap[k]);
}

function onHeadKeyUp(e: KeyboardEvent) {
  const k = e.key.toLowerCase();
  if (!headKeys.has(k)) return;

  headKeys.delete(k);
  sendHead("stop");
}

onMounted(() => {
  window.addEventListener("keydown", onHeadKeyDown);
  window.addEventListener("keyup", onHeadKeyUp);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onHeadKeyDown);
  window.removeEventListener("keyup", onHeadKeyUp);
});
</script>

<style scoped>
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
