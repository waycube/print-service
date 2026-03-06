import { createRouter, createWebHistory } from 'vue-router'
import GrocyView from './views/GrocyView.vue'
import OfficeView from './views/OfficeView.vue'

const routes = [
  { path: '/', redirect: '/grocy' },
  { path: '/grocy', component: GrocyView },
  { path: '/office', component: OfficeView }
]

export default createRouter({
  history: createWebHistory(),
  routes
})