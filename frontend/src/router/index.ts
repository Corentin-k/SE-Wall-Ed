import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import Home from "@/views/Home.vue";
import ColorPicker from "@/components/ColorPicker.vue";
import Temperature from "@/components/Camera.vue";

import Allcomponents from "@/views/Allcomponents.vue";
import Inwork from "@/components/inwork.vue";

const routes: Array<RouteRecordRaw> = [
  { path: "/", redirect: "/home" },
  { path: "/home", name: "Home", component: Home },
  { path: "/inwork", name: "InWork", component: Inwork },
  {
    path: "/motor",
    name: "Motor",
    component: () => import("@/components/CommandMotor.vue"),
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
