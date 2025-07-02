<template>
  <div id="app">
    <!-- Mobile Menu Toggle -->
    <!-- <div class="mobile-header">
      <div class="logo">🤖 Robot Control</div>
      <button
        class="mobile-menu-toggle"
        @click="toggleMobileMenu"
        :class="{ active: mobileMenuOpen }"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>

   
    <nav :class="{ 'mobile-open': mobileMenuOpen }">
      <div class="nav-container">
        <div class="nav-brand desktop-only">🤖 Robot Control</div>
        <div class="nav-links">
          <router-link to="/home" class="nav-item" @click="closeMobileMenu">
            <i class="icon">🏠</i>
            <span>Home</span>
          </router-link>
          <router-link to="/color" class="nav-item" @click="closeMobileMenu">
            <i class="icon">💡</i>
            <span>LED</span>
          </router-link>
          <router-link to="/camera" class="nav-item" @click="closeMobileMenu">
            <i class="icon">📹</i>
            <span>Camera</span>
          </router-link>
          <router-link to="/motor" class="nav-item" @click="closeMobileMenu">
            <i class="icon">🎮</i>
            <span>Motor</span>
          </router-link>
          <router-link
            to="/Allcomponents"
            class="nav-item"
            @click="closeMobileMenu"
          >
            <i class="icon">⚙️</i>
            <span>All</span>
          </router-link>
          <router-link
            to="/line_tracking"
            class="nav-item"
            @click="closeMobileMenu"
          >
            <i class="icon">🛤️</i>
            <span>Line</span>
          </router-link>
        </div>
      </div>
    </nav> -->

    <!-- Main Content -->
    <main class="main-content">
      <router-view></router-view>
    </main>

    <!-- Footer -->
    <!-- <footer>
      <div class="footer-content">
        <p>© 2024 Corentin-k</p>
        <p class="datetime">{{ currentDateTime }}</p>
      </div>
    </footer> -->

    <!-- Mobile Menu Overlay -->
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
  background-color: var(--surface-color);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  position: sticky;
  top: 0;
  z-index: 1000;
  border-radius: 11px;
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
  align-items: center;
  margin-left: auto;
  gap: 0.5rem;
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
  padding: 2rem 1rem;
  max-width: 1200px;
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
  z-index: 999;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.mobile-overlay.active {
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

/* Responsive Design */
@media (max-width: 768px) {
  .mobile-header {
    display: flex;
  }

  .desktop-only {
    display: none;
  }

  nav {
    position: fixed;
    top: 70px;
    left: -100%;
    width: 280px;
    height: calc(100vh - 70px);
    background-color: var(--surface-color);
    transition: left 0.3s ease;
    z-index: 1000;
    border-right: 1px solid var(--border-color);
  }

  nav.mobile-open {
    left: 0;
  }

  nav.mobile-open ~ .mobile-overlay {
    display: block;
  }

  .nav-container {
    flex-direction: column;
    align-items: stretch;
    padding: 0;
    height: 100%;
    border-radius: 10px;
  }

  .nav-links {
    flex-direction: column;
    margin: 0;
    gap: 0;
    padding: 1rem 0;
  }

  .nav-item {
    padding: 1rem 1.5rem;
    border-radius: 0;
    border-bottom: 1px solid var(--border-color);
    justify-content: flex-start;
  }

  .nav-item:hover {
    transform: none;
    background-color: rgba(187, 134, 252, 0.1);
    color: var(--primary-color);
  }

  .main-content {
    padding: 1rem;
    margin-top: 70px;
  }

  .footer-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 0.5rem;
  }

  .nav-item span {
    font-size: 0.9rem;
  }

  .logo {
    font-size: 1rem;
  }
}
</style>
