<template>
  <div class="color-picker">
    <h2>LED Strip Control</h2>

    <div class="color-display" :style="{ backgroundColor: displayColor }"></div>

    <input
      type="color"
      v-model="selectedColor"
      @input="updateColor"
      class="color-input"
    />

    <div class="intensity-control">
      <label for="intensity">Intensity:</label>
      <input
        type="range"
        id="intensity"
        v-model="intensity"
        min="0"
        max="100"
        @input="updateColor"
        class="intensity-slider"
      />
      <span>{{ intensity }}%</span>
    </div>

    <button @click="sendColor" class="apply-button">Apply Color</button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "ColorPicker",
  data() {
    return {
      selectedColor: "#ff0000",
      intensity: 100,
      displayColor: "#ff0000",
      connected: false,
      error: false,
      loading: true,
    };
  },
  methods: {
    // Fonction pour mettre à jour la couleur d'affichage en fonction de la couleur sélectionnée et de l'intensité
    updateColor() {
      const rgb = this.hexToRgb(this.selectedColor);
      if (rgb) {
        const adjustedRgb = this.adjustIntensity(rgb, this.intensity);
        this.displayColor = this.rgbToHex(adjustedRgb);
      }
    },
    // Fonction pour convertir une couleur hexadécimale en RGB
    hexToRgb(hex: string): [number, number, number] | null {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result
        ? [
            parseInt(result[1], 16),
            parseInt(result[2], 16),
            parseInt(result[3], 16),
          ]
        : null;
    },
    rgbToHex(rgb: [number, number, number]): string {
      return (
        "#" +
        rgb
          .map((x) => {
            const hex = x.toString(16);
            return hex.length === 1 ? "0" + hex : hex;
          })
          .join("")
      );
    },
    // Fonction pour ajuster l'intensité de la couleur
    adjustIntensity(
      rgb: [number, number, number],
      intensity: number
    ): [number, number, number] {
      const factor = intensity / 100;
      return rgb.map((channel) => Math.round(channel * factor)) as [
        number,
        number,
        number
      ];
    },
    async sendColor() {
      console.log("Envoi de la couleur :", this.displayColor);
      try {
        const response = await fetch("http://10.3.208.73:5000/led/color", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            color: this.displayColor,
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          console.error("Erreur côté serveur :", error);
          alert("Erreur : " + error.error);
        } else {
          const result = await response.json();
          console.log("Succès :", result);
        }
      } catch (err) {
        console.error("Erreur réseau :", err);
        alert("Erreur de connexion au robot.");
      }
    },
  },
  // Fonction pour rafraîchir les données
  refreshData() {
    this.updateColor();
  },

  mounted() {
    // Initialisation de la couleur d'affichage avec la couleur sélectionnée par défaut lorsqu'on ouvre la page
    // et vérification de la connexion avec l'ESP32
    this.updateColor();
  },
});
</script>

<style scoped>
:root {
  --default-color: #bb86fc;
}
.color-picker {
  background-color: #1e1e1e;
  border-radius: 10px;
  padding: 2rem;
  max-width: 300px;
  margin: 2rem auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  color: #03dac6;
  margin-bottom: 1.5rem;
}

.color-display {
  width: 100%;
  height: 100px;
  border-radius: 5px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 255, 255, 1);
  }
  100% {
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  }
}

.color-input {
  width: 100%;
  height: 40px;
  border: none;
  outline: none;
  cursor: pointer;
  margin-bottom: 1rem;
}

.disabled-color-input {
  opacity: 0.5;
  cursor: not-allowed;
  animation: none;
}

.intensity-control {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.intensity-slider {
  flex-grow: 1;
  margin: 0 1rem;
}

.apply-button {
  width: 100%;
  padding: 0.75rem;
  color: #121212;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: background-color 0.3s;
}

.apply-button {
  background-color: var(--default-color);
}

.apply-button:hover {
  background-color: var(--default-color) + "#9969da";
}
</style>
