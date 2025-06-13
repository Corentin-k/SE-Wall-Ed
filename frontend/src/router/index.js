import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import ColorPicker from "@/components/ColorPicker.vue";
import Temperature from "@/components/Camera.vue";
import CommandMotor from "@/components/CommandMotor.vue";
import Allcomponents from "@/views/Allcomponents.vue";

const routes = [
  { path: "/", redirect: "/home" },
  { path: "/home", name: "Home", component: Home },
  {
    path: "/motor",
    name: "Motor",
    component: CommandMotor,
  },
  { path: "/color", name: "ColorPicker", component: ColorPicker },
  { path: "/temperature", name: "Temperature", component: Temperature },
  { path: "/allcomponents", name: "Allcomponents", component: Allcomponents },
];

const index = createRouter({
  history: createWebHistory(),
  routes,
});

export default index;
