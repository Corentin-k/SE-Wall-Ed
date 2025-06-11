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

const headKeys = reactive(new Set<string>()); // Garde une trace des touches actuellement enfoncées

// Fonction pour envoyer la commande combinée au serveur
async function sendCombinedHeadCommand() {
  let pan = 0;
  let tilt = 0;

  // Détermine la direction de pan et tilt basée sur les touches enfoncées
  if (headKeys.has('l')) { // L pour Pan Right
    pan = 1;
  } else if (headKeys.has('j')) { // J pour Pan Left
    pan = -1;
  }

  if (headKeys.has('i')) { // I pour Tilt Up
    tilt = 1;
  } else if (headKeys.has('k')) { // K pour Tilt Down
    tilt = -1;
  }

  // --- LOGS ADDED IN VUE.JS ---
  console.log(`[Vue.js] Current headKeys: ${Array.from(headKeys).join(', ')}`);
  console.log(`[Vue.js] Calculated pan: ${pan}, tilt: ${tilt}`);
  // --- END LOGS ADDED ---

  // Si aucune touche de mouvement n'est enfoncée, arrêter le mouvement
  if (pan === 0 && tilt === 0) {
    console.log("[Vue.js] Sending servo/stop command."); // Log additionnel
    await axios.post("http://10.3.208.73:5000/servo/stop")
      .then(response => console.log("[Vue.js] Servo stop success:", response.data))
      .catch(error => console.error("[Vue.js] Servo stop error:", error));
  } else {
    console.log(`[Vue.js] Sending servo/start command with {pan: ${pan}, tilt: ${tilt}}.`); // Log additionnel
    await axios.post("http://10.3.208.73:5000/servo/start", { pan, tilt })
      .then(response => console.log("[Vue.js] Servo start success:", response.data))
      .catch(error => console.error("[Vue.js] Servo start error:", error));
  }
}

function onHeadKeyDown(e: KeyboardEvent) {
  const k = e.key.toLowerCase();
  const validKeys = ["i", "j", "k", "l"];

  if (!validKeys.includes(k) || headKeys.has(k)) {
    return; // Ignorer si la touche n'est pas pertinente ou est déjà enfoncée
  }

  headKeys.add(k); // Ajouter la touche aux touches enfoncées
  console.log(`[Vue.js] KeyDown: ${k}, headKeys now: ${Array.from(headKeys).join(', ')}`); // Log additionnel
  sendCombinedHeadCommand(); // Envoyer la nouvelle commande combinée
}

function onHeadKeyUp(e: KeyboardEvent) {
  const k = e.key.toLowerCase();
  
  if (!headKeys.has(k)) {
    return; // Ignorer si la touche n'était pas enfoncée
  }

  headKeys.delete(k); // Retirer la touche des touches enfoncées
  console.log(`[Vue.js] KeyUp: ${k}, headKeys now: ${Array.from(headKeys).join(', ')}`); // Log additionnel
  sendCombinedHeadCommand(); // Envoyer la nouvelle commande combinée (pour arrêter ou ajuster le mouvement)
}

onMounted(() => {
  window.addEventListener("keydown", onHeadKeyDown);
  window.addEventListener("keyup", onHeadKeyUp);
  console.log("[Vue.js] Head command listeners mounted."); // Log additionnel
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onHeadKeyDown);
  window.removeEventListener("keyup", onHeadKeyUp);
  console.log("[Vue.js] Head command listeners unmounted."); // Log additionnel
});
</script>

<style scoped>
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