import { createApp } from 'vue'
import App from './App.vue'

import { library } from '@fortawesome/fontawesome-svg-core'
import {faExpandAlt, faRunning, faStopwatch20, faSun, faThermometerHalf} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faStopwatch20)
library.add(faSun)
library.add(faRunning)
library.add(faExpandAlt)
library.add(faThermometerHalf)

createApp(App)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
