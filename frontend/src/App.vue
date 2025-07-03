<template>
  <div id="app">
    <div class="mobile-nav-wrapper">
      <button
        class="mobile-menu-toggle"
        @click="toggleMobileMenu"
        :class="{ active: mobileMenuOpen }"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav :class="{ 'mobile-open': mobileMenuOpen }">
        <div class="nav-container">
          <div class="nav-links">
            <router-link to="/home" class="nav-item" @click="closeMobileMenu">
              <i class="icon">🏠</i><span>Home</span>
            </router-link>
            <router-link to="/color" class="nav-item" @click="closeMobileMenu">
              <i class="icon">💡</i><span>LED</span>
            </router-link>
            <router-link to="/camera" class="nav-item" @click="closeMobileMenu">
              <i class="icon">📹</i><span>Camera</span>
            </router-link>
            <router-link to="/motor" class="nav-item" @click="closeMobileMenu">
              <i class="icon">🎮</i><span>Motor</span>
            </router-link>
            <router-link to="/Mode" class="nav-item" @click="closeMobileMenu">
              <i class="icon">🛤️</i><span>Modes</span>
            </router-link>
            <router-link
              to="/Allcomponents"
              class="nav-item"
              @click="closeMobileMenu"
            >
              <i class="icon">⚙️</i><span>All</span>
            </router-link>
          </div>
        </div>
      </nav>
    </div>

    <!-- Main Content -->
    <main class="main-content">
      <router-view></router-view>
    </main>
    <div
      class="mobile-overlay"
      :class="{ active: mobileMenuOpen }"
      @click="closeMobileMenu"
    ></div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";

export default defineComponent({
  name: "App",
  setup() {
    const currentDateTime = ref(new Date().toLocaleString());
    const mobileMenuOpen = ref(false);

    const updateCurrentDateTime = () => {
      currentDateTime.value = new Date().toLocaleString();
    };

    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value;
    };

    const closeMobileMenu = () => {
      mobileMenuOpen.value = false;
    };

    onMounted(() => {
      const interval = setInterval(updateCurrentDateTime, 1000);
      return () => clearInterval(interval);
    });

    return {
      currentDateTime,
      mobileMenuOpen,
      toggleMobileMenu,
      closeMobileMenu,
    };
  },
});
</script>

<style>
:root {
  --primary-color: #bb86fc;
  --secondary-color: #03dac6;
  --background-color: #121212;
  --surface-color: #1e1e1e;
  --error-color: #cf6679;
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --border-color: rgba(255, 255, 255, 0.12);

  /* Responsive breakpoints */
  --mobile: 768px;
  --tablet: 1024px;
  --desktop: 1200px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--background-color);
  color: var(--text-primary);
  font-family: "Roboto", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

/* Mobile Header */
.mobile-header {
  display: none;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--surface-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1001;
  border-radius: 11px;
}

.logo {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--primary-color);
}

.mobile-menu-toggle {
  position: fixed;
  top: 15px;
  right: 15px;
  z-index: 1100;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 30px;
  height: 30px;
  justify-content: center;
}

.mobile-menu-toggle span {
  display: block;
  height: 3px;
  width: 100%;
  background-color: var(--text-primary);
  transition: all 0.3s ease;
  transform-origin: center;
}

.mobile-menu-toggle.active span:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.mobile-menu-toggle.active span:nth-child(2) {
  opacity: 0;
}

.mobile-menu-toggle.active span:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

/* Navigation */
nav {
  position: fixed;
  top: 0;
  left: -280px; /* caché par défaut */
  width: 280px;
  height: 100vh;
  background-color: var(--surface-color);
  transition: left 0.3s ease;
  z-index: 1001;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
  border-right: 1px solid var(--border-color);
  padding-top: 70px; /* pour éviter de cacher le bouton */
}

nav.mobile-open {
  left: 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 1rem;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
  padding: 1rem 0;
}

.nav-links {
  display: flex;
  flex-direction: column; /* ← chaque élément sur une ligne */
  align-items: stretch;
}

.nav-item {
  color: var(--text-secondary);
  text-decoration: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.nav-item:hover {
  background-color: var(--primary-color);
  color: var(--background-color);
  transform: translateY(-2px);
}

.nav-item.router-link-active {
  background-color: var(--primary-color);
  color: var(--background-color);
}

.icon {
  font-size: 1.2rem;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 0 2rem 1rem;
  margin: 0 auto;
  width: 100%;
}

/* Footer */
footer {
  background-color: var(--surface-color);
  border-top: 1px solid var(--border-color);
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-secondary);
}

.datetime {
  font-family: "Courier New", monospace;
  font-size: 0.9rem;
}

/* Mobile Overlay */
.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.mobile-overlay.active {
  display: block;
  opacity: 1;
}

/* Button Styles */
button {
  background-color: var(--surface-color);
  color: var(--primary-color);
  border: 1px solid var(--border-color);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
}

button:hover {
  background-color: var(--primary-color);
  color: var(--background-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(187, 134, 252, 0.3);
}

button:active {
  transform: translateY(0);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Cacher le menu mobile complet sur les grands écrans */
.mobile-nav-wrapper {
  display: none;
}

@media (max-width: 1500px) {
  .mobile-nav-wrapper {
    display: block;
  }
}
</style>
