import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'

import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'

import App from './App.vue'
import './style.css'
import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
})

app.component('PButton', Button)
app.component('PCard', Card)
app.component('PInputText', InputText)
app.component('PSelect', Select)
app.component('PCheckbox', Checkbox)
app.component('PMessage', Message)
app.component('PProgressSpinner', ProgressSpinner)

app.mount('#app')
