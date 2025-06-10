<template>
  <div class="color-picker">
    <h2>
      LED Strip Control
      <font-awesome-icon
        v-if="connected"
        :icon="['fas', 'check']"
        class="connected-icon"
      />
      <font-awesome-icon
        v-else
        :icon="['fas', 'xmark']"
        class="disconnected-icon"
      />
    </h2>

    <div
      class="color-display"
      :style="{ backgroundColor: displayColor }"
      :class="{ 'disabled-color-input': !connected }"
    ></div>

    <input
      type="color"
      v-model="selectedColor"
      @input="updateColor"
      class="color-input"
      :disabled="!connected"
      :class="{ 'disabled-color-input': !connected }"
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
        :disabled="!connected"
        :class="{ 'disabled-color-input': !connected }"
      />
      <span>{{ intensity }}%</span>
    </div>

    <button v-if="error" @click="refreshData" class="refresh-button">
      <font-awesome-icon :icon="['fas', 'sync-alt']" /> Refresh
    </button>
    <button v-if="loading" disabled class="loading-button">
      <font-awesome-icon :icon="['fas', 'spinner']" spin /> Loading...
    </button>
    <button
      v-else
      @click="sendColor"
      class="apply-button"
      :disabled="!connected"
    >
      Apply Color
    </button>
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

    // Fonction pour envoyer la couleur sélectionnée à l'ESP32

    async sendColor() {
      this.loading = true;
      this.error = false;
      try {
        this.connected = true;
        console.log("Color set successfully");
      } catch (error) {
        console.error("Error setting color:", error);
        this.error = true;
      } finally {
        this.loading = false;
      }
    },

    // Fonction pour vérifier la connexion avec l'ESP32
    async checkConnection() {
      this.loading = true;
      this.error = false;
      try {
        this.connected = true;
        console.log("ESP32 is connected");
      } catch (error) {
        console.error("ESP32 is not connected:", error);
        this.error = true;
        this.connected = false;
      } finally {
        this.loading = false;
      }
    },
    // Fonction pour rafraîchir les données
    refreshData() {
      this.error = false;
      this.loading = true;
      this.connected = false;
      this.updateColor();
      this.checkConnection();
    },
  },
  mounted() {
    // Initialisation de la couleur d'affichage avec la couleur sélectionnée par défaut lorsqu'on ouvre la page
    // et vérification de la connexion avec l'ESP32
    this.updateColor();
    this.checkConnection();
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

.connected-icon {
  color: #03dac6;
}

.disconnected-icon {
  color: #ff5252;
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

.apply-button,
.refresh-button,
.loading-button {
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

.refresh-button {
  background-color: #03dac6;
  margin-bottom: 1rem;
}

.refresh-button:hover {
  background-color: #00b3a6;
}

.loading-button {
  background-color: #ffca28;
}
</style>
