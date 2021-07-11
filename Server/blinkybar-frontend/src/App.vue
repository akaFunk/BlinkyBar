<template>
  <div class="app">
    <div class="image-box">
      <div v-if="progress_status==='ready'">
        <file-uploader upload-url="/set_image">
          <img :src="resultUrl + image_hash" :key="image_hash" alt="scaled image stored on the BlinkyBar"/>
        </file-uploader>
      </div>
      <div v-if="progress_status==='noimage'">
        <p>No image uploaded.</p>
      </div>
      <div v-if="progress_status === 'processing' || progress_status === 'playing'">
        <ve-progress :progress="progress_value*100" empty-color="#e1e1e1" color="#69c0ff" :size="80">
          <legend>{{ progress_percent }} %</legend>
        </ve-progress>
        <p>{{ progress_msg }}...</p>
      </div>
    </div>
    <slider-input v-if="!isNaN(speed)" icon="running" v-model="speed" :min="0.1" :max="10" :interval="0.1" unit="m/s"/>
    <slider-input v-if="!isNaN(brightness)" icon="sun" v-model="brightness" :min="1" :max="100" :interval="1" unit="%"
                  :scaling-factor="100"/>
    <slider-input v-if="!isNaN(trigger_delay)" icon="stopwatch-20" v-model="trigger_delay" :min="0" :max="60"
                  :interval="1" unit="s"/>
    <slider-input v-if="!isNaN(color_temperature)" icon="thermometer-half" v-model="color_temperature" :min="1000"
                  :max="10000"
                  :interval="100" unit="K"/>
    <toggle-switch caption="Mirror" icon="arrows-alt-h" v-model="mirror"/>
    <toggle-switch caption="Repeat" icon="redo" v-model="repeat"/>
    <toggle-switch caption="Allow scaling" icon="expand-alt" v-model="allow_scaling"/>

    <button class="push-btn" @click="trigger">
      <font-awesome-icon :icon="['fas','play']"/>
      Play
    </button>
    <hr/>
    <h3>Debug info</h3>
    Speed: {{ speed }} <br/>
    Brightness: {{ brightness }}<br/>
    Trigger delay: {{ trigger_delay }}<br/>
    Mirror: {{ mirror }}<br/>
    Repeat: {{ repeat }}<br/>
    Allow scaling: {{ allow_scaling }}<br/>
    Progress status: {{ progress_status }}<br/>
    Progress value: {{ progress_value }}<br/>
    Progress msg: {{ progress_msg }}<br/>
  </div>
</template>

<script>
import SliderInput from "@/components/SliderInput";
import ToggleSwitch from "@/components/ToggleSwitch";
import FileUploader from "@/components/FileUploader";
import {VeProgress} from "vue-ellipse-progress";

let printf = require('printf');

export default {
  name: 'App',
  components: {
    SliderInput,
    ToggleSwitch,
    FileUploader,
    VeProgress,
    /*  Accordion,
      AccordionPanel,
      AccordionPanelHeader,
      AccordionPanelContent,*/
  },
  data: function () {
    return {
      resultUrl: "/get_image_scaled?fake_param=",
      settingsUrl: "/settings",
      speed: NaN,
      brightness: NaN,
      trigger_delay: NaN,
      mirror: false,
      allow_scaling: true,
      repeat: false,
      color_temperature: NaN,
      image_hash: '',
      progress_status: '',
      progress_value: 0,
      progress_percent: 0,
      progress_msg: '',
      timer: setInterval(this.updateSettings, 200),
      updateQueryList: {},
      blockUpdate: false,
      lastTime: 0,
    }
  },
  methods: {
    async updateSettings() {
      let url = new URL(document.location.href + this.settingsUrl);
      Object.keys(this.updateQueryList).forEach(key => url.searchParams.append(key, this.updateQueryList[key]))
      this.updateQueryList = {}
      let resp = await fetch(url);
      let data = await resp.json();
      this.processNewData(data);
      this.blockUpdate = false;
    },
    processNewData(data) {
      this.image_hash = data.image_hash;
      this.progress_status = data.progress_status;
      this.progress_value = data.progress_value;
      this.progress_msg = data.progress_msg;
      this.progress_percent = printf('%.1f', this.progress_value * 100);

      // If blockUpdate is true, one of the user inputs has been modified and we don't want to overwrite that with an old value
      if (!this.blockUpdate) {
        this.speed = data.speed;
        this.brightness = data.brightness;
        this.trigger_delay = data.trigger_delay;
        this.mirror = data.mirror;
        this.repeat = data.repeat;
        this.allow_scaling = data.allow_scaling;
        this.color_temperature = data.color_temperature;
      }
    },
    update(param, value) {
      this.blockUpdate = true;
      this.updateQueryList[param] = value;
    },
    async trigger() {
      let url = new URL(document.location.href + this.triggerCmd);
      await fetch(url);
    },
  },
  watch: {
    speed(newVal, oldVal) {
      if (!isNaN(oldVal)) {
        this.update('speed', newVal);
      }
    },
    brightness(newVal, oldVal) {
      if (!isNaN(oldVal)) {
        this.update('brightness', newVal);
      }
    },
    trigger_delay(newVal, oldVal) {
      if (!isNaN(oldVal)) {
        this.update('trigger_delay', newVal);
      }
    },
    color_temperature(newVal, oldVal) {
      if (!isNaN(oldVal)) {
        this.update('color_temperature', newVal);
      }
    },
    mirror(newVal) {
      this.update('mirror', newVal);
    },
    repeat(newVal) {
      this.update('repeat', newVal);
    },
    allow_scaling(newVal) {
      this.update('allow_scaling', newVal);
    },
  },
  created() {
    this.updateSettings();
  }
}
</script>

<style>
.app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
  width: 100%;
  max-width: 500px;
  margin-left: 1vw;
  margin-right: 1vw;
}

.image-box {
  text-align: center;
  min-height: 13vh;
}

img {
  image-rendering: pixelated;
}

.push-btn {
  background-color: #9cd5ff;
  border-radius: 3px;
  border: 1px solid #0b0e07;
  display: inline-block;
  cursor: pointer;
  color: #000000;
  font-size: 15px;
  padding: 9px 23px;
  margin-top: 2vh;
  text-decoration: none;
  text-shadow: 0 1px 0 #cddeff;
  width: 100%;
}

.push-btn:hover {
  background-color: #69c1ff;
}

.push-btn:active {
  position: relative;
  top: 1px;
}
</style>
