import { createApp } from 'vue'
import App from './App.vue'

import { library } from '@fortawesome/fontawesome-svg-core'
import {
    faExpandAlt,
    faPlay,
    faRunning,
    faStopwatch20,
    faSun,
    faThermometerHalf,
    faArrowsAltH,
    faRedo
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faStopwatch20)
library.add(faSun)
library.add(faRunning)
library.add(faExpandAlt)
library.add(faThermometerHalf)
library.add(faPlay)
library.add(faArrowsAltH)
library.add(faRedo)

createApp(App)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
