<template>
  <div class="home">
    <h1>Bonjour. Je suis Baymax</h1>
    <p>Votre assistant de santé personnel</p>
    <Vue3Lottie
      animation-link="https://assets2.lottiefiles.com/packages/lf20_GbabwrUY2k.json"
      :height="200"
      :width="200"
    />

    <div class="feature-grid">
      <router-link to="/color" class="feature-item">
        <div>
          <h3>LED Control</h3>
          <p>Control the LED lights on the robot.</p>
        </div>
      </router-link>

      <router-link to="/temperature" class="feature-item">
        <div>
          <h3>Temperature Monitoring</h3>
          <p>Monitor the temperature inside the robot.</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "Home",
});
</script>

<style scoped>
.home {
  padding: 2rem;
  text-align: center;
}

h1 {
  color: var(--default-color);
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

p {
  color: #b0b0b0;
  max-width: 600px;
  margin: 0 auto 2rem;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.feature-item {
  background-color: #1e1e1e;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
  text-decoration: none;
}

.feature-item:hover {
  transform: translateY(-5px);
}

.feature-item h3 {
  color: #03dac6;
  margin-bottom: 0.5rem;
}

.feature-item p {
  color: #b0b0b0;
  font-size: 0.9rem;
}
</style>
