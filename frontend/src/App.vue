<template>
  <div id="app">
    <nav>
      <router-link to="/home" class="nav-item">Home</router-link>
      <router-link to="/color" class="nav-item">LED Control</router-link>
      <router-link to="/temperature" class="nav-item">Temperature</router-link>
      <router-link to="/motor" class="nav-item">Motor</router-link>
      <router-link to="/Allcomponents" class="nav-item">All</router-link>
    </nav>
    <router-view></router-view>

    <footer>
      <p>© 2024 Corentin-k</p>
      <p>{{ currentDateTime }}</p>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";

export default defineComponent({
  name: "App",
  setup() {
    const currentDateTime = ref(new Date().toLocaleString());

    const updateCurrentDateTime = () => {
      currentDateTime.value = new Date().toLocaleString();
    };

    onMounted(() => {
      const interval = setInterval(updateCurrentDateTime, 1000);
      return () => clearInterval(interval);
    });

    return {
      currentDateTime,
    };
  },
});
</script>

<style>
:root {
  --default-color: #bb86fc;
}

nav {
  background-color: #1e1e1e;
  padding: 1rem;
  display: flex;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-item {
  color: var(--default-color);
  text-decoration: none;
  padding: 0.5rem 1rem;
  margin: 0 0.5rem;
  border-radius: 5px;
  transition: background-color 0.3s, color 0.3s;
}

button {
  color: var(--default-color);
  text-decoration: none;
  padding: 0.5rem 1rem;
  margin: 0 0.5rem;
  border-radius: 5px;
  transition: background-color 0.3s, color 0.3s;
  background-color: #1e1e1e;
  border: none;
  cursor: pointer;
  font-size: large;
}

.nav-item:hover,
.nav-item {
  background-color: var(--default-color);
  color: #121212;
}

footer {
  background-color: #1e1e1e;
  padding: 1rem;
  text-align: center;
  margin-top: auto;
}

.right-item {
  margin-left: auto;
}
</style>
