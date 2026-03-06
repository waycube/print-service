import { createRouter, createWebHistory } from "vue-router"
import HomeView from "./views/HomeView.vue"
import GrocyView from "./views/GrocyView.vue"
import WaycubeView from "./views/WaycubeView.vue"

const routes = [
  { path: "/", component: HomeView },
  { path: "/grocy", component: GrocyView },
  { path: "/waycube", component: WaycubeView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router