import { createApp } from 'vue'
import App from './App.vue'

import { library } from '@fortawesome/fontawesome-svg-core'
import {faExpandAlt, faRunning, faStopwatch20, faSun} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faStopwatch20)
library.add(faSun)
library.add(faRunning)
library.add(faExpandAlt)

createApp(App)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
