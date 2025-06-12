<template>
  <div class="columns">
    <!-- Colonne 1 -->
    <div class="column">
      <Camera />
      <Lidar />
      <ColorPicker />
    </div>

    <!-- Colonne 2 -->
    <div class="column">
      <CommandHead />
      <CommandMotor />
      <Mode />
    </div>

    <!-- Colonne 3 -->
    <div class="column">
      <Settings />
      <!-- tu peux ajouter d’autres composants ici si besoin -->
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
  },
});
</script>

<style scoped>
.columns {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  box-sizing: border-box;
}

.column {
  flex: auto;
  flex-direction: column;

  align-items: stretch;
}

.column {
  min-height: 200px;
}
</style>
