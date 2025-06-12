import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./router"; // <-- Assure-toi que cet import existe

createApp(App).use(router).mount("#app");
