import { createRouter, createWebHistory } from "vue-router"
import HomeView from "./views/HomeView.vue"
import GrocyView from "./views/GrocyView.vue"
import OfficeView from "./views/OfficeView.vue"

const routes = [
  { path: "/", component: HomeView },
  { path: "/grocy", component: GrocyView },
  { path: "/office", component: OfficeView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router