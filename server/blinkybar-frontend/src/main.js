import { createApp } from 'vue'
import App from './App.vue'

import { library } from '@fortawesome/fontawesome-svg-core'
import {
    faExpandAlt,
    faPlay,
    faStop,
    faTimes,
    faRunning,
    faStopwatch20,
    faSun,
    faThermometerHalf,
    faArrowsAltH,
    faRedo,
    faEllipsisH
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faStopwatch20)
library.add(faSun)
library.add(faRunning)
library.add(faExpandAlt)
library.add(faThermometerHalf)
library.add(faPlay)
library.add(faStop)
library.add(faTimes)
library.add(faArrowsAltH)
library.add(faRedo)
library.add(faEllipsisH)

createApp(App)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
