<template>
  <div class="columns">
    <!-- Colonne 1 -->
    <div class="column">
      <Camera />
      <Radar class="radar" />     
    </div>

    <!-- Colonne 2 -->
     <div class="column">
      <CommandHead />
      <CommandMotor />
    </div> 

    <!-- Colonne 3 -->
    <div class="column">
      <Mode />
      <ColorPicker class="color-picker" />
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
import Radar from "../components/RadarChart.vue";
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
.color-picker {
  transform: scale(0.7);
}
.radar {
  transform: scale(0.8);
}
</style>
