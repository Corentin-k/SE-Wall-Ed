<template>
  <div class="settings">
    <h2>Settings</h2>
    <p>Set speed</p>
    <input type="number" v-model.number="speed" />

    <button @click="updateSpeed">Update Speed</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";

// on utilise un ref pour la vitesse
const speed = ref<number>(50);

async function updateSpeed() {
  try {
    // on envoie la valeur du ref directement
    const response = await axios.post(
      `${import.meta.env.VITE_ROBOT_BASE_URL}/robot/speed`,
      {
        speed: speed.value,
      }
    );
    console.log(response.data.message);
  } catch (error: any) {
    console.error(
      "Error updating speed:",
      error.response?.data || error.message
    );
  }
}
</script>

<style scoped>
:root {
  --default-color: #bb86fc;
}

.settings {
  background-color: #1e1e1e;
  border-radius: 10px;
  padding: 2rem;
  max-width: 350px;
  margin: 2rem auto;
  color: #e0e0e0;
  height: 80%;
}

input[type="number"] {
  width: 100%;
  padding: 0.5rem;
  margin: 1rem 0;
  border-radius: 4px;
  border: 1px solid #444;
  background: #2a2a2a;
  color: #e0e0e0;
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
  margin-bottom: 1rem;
}

button:focus {
  outline: 3px solid #bb86fc;
  outline-offset: 2px;
}
</style>
