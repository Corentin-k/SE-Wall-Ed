import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import ColorPicker from "@/components/ColorPicker.vue";
import Camera from "@/components/Camera.vue";
import CommandMotor from "@/components/CommandMotor.vue";
import Allcomponents from "@/views/Allcomponents.vue";
import Mode from "@/components/Mode.vue";

const routes = [
  { path: "/", redirect: "/allcomponents" },
  { path: "/home", name: "Home", component: Home },
  {
    path: "/motor",
    name: "Motor",
    component: CommandMotor,
  },
  { path: "/color", name: "ColorPicker", component: ColorPicker },
  { path: "/camera", name: "Camera", component: Camera },
  { path: "/allcomponents", name: "Allcomponents", component: Allcomponents },
  { path: "/line_tracking", name: "LineTracking", component: Mode },
  { path: "/mode", name: "Mode", component: Mode },
];

const index = createRouter({
  history: createWebHistory(),
  routes,
});

export default index;
