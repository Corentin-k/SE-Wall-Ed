<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>🤖 DashBoard</h1>
      <p>Control the robot !</p>
    </div>

    <div class="dashboard-grid">
      <!-- Section Caméra et Radar -->
      <div class="grid-section camera-section">
        <Camera />
        <Radar class="radar-chart" />
      </div>

      <!-- Section Contrôles -->
      <div class="grid-section controls-section">
        <CommandHead />
        <CommandMotor />
      </div>

      <!-- Section Modes et Couleurs -->
      <div class="grid-section modes-section">
        <Mode />
        <ColorPicker class="color-picker" />
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue";
import Camera from "../components/Camera.vue";
import CommandHead from "../components/CommandHead.vue";
import CommandMotor from "../components/CommandMotor.vue";
import Lidar from "../components/Lidar.vue";
import Settings from "../components/Settings.vue";
import Mode from "../components/Mode.vue";
import ColorPicker from "../components/ColorPicker.vue";
import Radar from "../components/RadarChartLive.vue";
export default defineComponent({
  name: "Allcomponents",
  components: {
    Camera,
    CommandHead,
    CommandMotor,
    Lidar,
    Settings,
    Mode,
    ColorPicker,
    Radar,
  },
});
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  margin: 0 auto;
  padding: 1rem;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: linear-gradient(
    135deg,
    var(--primary-color, #bb86fc) 0%,
    var(--secondary-color, #03dac6) 100%
  );
  border-radius: 16px;
  color: var(--background-color, #121212);
}

.dashboard-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.dashboard-header p {
  font-size: 1.1rem;
  opacity: 0.8;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  align-items: start;
}

.grid-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Responsive adjustments for components */
.radar-chart {
  transform: scale(0.9);
  transform-origin: top center;
}

.color-picker {
  transform: scale(0.8);
  transform-origin: top center;
}

/* Tablet responsive */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 1.5rem;
  }

  .dashboard-header h1 {
    font-size: 2rem;
  }

  .dashboard-header p {
    font-size: 1rem;
  }

  .radar-chart {
    transform: scale(0.85);
  }

  .color-picker {
    transform: scale(0.75);
  }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .dashboard {
    padding: 0.5rem;
  }

  .dashboard-header {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .dashboard-header h1 {
    font-size: 1.8rem;
  }

  .dashboard-header p {
    font-size: 0.9rem;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .grid-section {
    gap: 1rem;
  }

  .radar-chart {
    transform: scale(0.8);
  }

  .color-picker {
    transform: scale(0.7);
  }
}

/* Small mobile */
@media (max-width: 520px) {
  .dashboard {
    padding: 0.25rem;
  }

  .dashboard-header {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .dashboard-header h1 {
    font-size: 1.5rem;
  }

  .dashboard-header p {
    font-size: 0.85rem;
  }

  .dashboard-grid {
    gap: 0.75rem;
  }

  .grid-section {
    gap: 0.75rem;
  }

  .radar-chart {
    transform: scale(0.75);
  }

  .color-picker {
    transform: scale(0.65);
  }
}

/* Extra small devices */
@media (max-width: 400px) {
  .dashboard-header h1 {
    font-size: 1.3rem;
  }

  .radar-chart {
    transform: scale(0.7);
  }

  .color-picker {
    transform: scale(0.6);
  }
}
</style>
