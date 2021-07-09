<template>
  <div class="app">
    <slider-input caption="&#x1F3c3;" v-model="speed" :min="0.1" :max="10" :interval="0.1" unit="m/s"/>
    <slider-input caption="&#x1F506;" v-model="brightness" :min="1" :max="100" :interval="1" unit="%"
                  :scaling-factor="100"/>
    <slider-input caption="&#9201;" v-model="trigger_delay" :min="0" :max="60" :interval="1" unit="s"/>
    <toggle-switch caption="Allow scaling" v-model="allow_scaling"/>
    <file-uploader upload-url="/set_image"/>

    <div>
      <div v-if="progress_status==='ready'">
        <img :src="resultUrl + image_hash" :key="image_hash" alt="scaled image stored on the BlinkyBar"/>
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

    <hr/>
    <h3>Debug info</h3>
    Speed: {{ speed }} <br/>
    Brightness: {{ brightness }}<br/>
    Trigger delay: {{ trigger_delay }}<br/>
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
      speed: 0,
      brightness: 0,
      trigger_delay: 0,
      allow_scaling: true,
      image_hash: '',
      progress_status: '',
      progress_value: 0,
      progress_percent: 0,
      progress_msg: '',
      timer: setInterval(this.fetchData, 200),
    }
  },
  methods: {
    fetchData() {
      fetch(this.settingsUrl)
          .then(response => response.json())
          .then(data => this.processNewData(data));
    },
    processNewData(data) {
      this.speed = data.speed;
      this.brightness = data.brightness;
      this.trigger_delay = data.trigger_delay;
      this.allow_scaling = data.allow_scaling;
      this.image_hash = data.image_hash;
      this.progress_status = data.progress_status;
      this.progress_value = data.progress_value;
      this.progress_msg = data.progress_msg;
      this.progress_percent = printf('%.1f', this.progress_value * 100);
    },
    update(param, value) {
      console.log(this.settingsUrl + '?' + param + '=' + value);
      fetch(this.settingsUrl + '?' + param + '=' + value);
    }
  },
  watch: {
    speed(newVal) {
      this.update('speed', newVal);
    },
    brightness(newVal) {
      this.update('brightness', newVal);
    },
    trigger_delay(newVal) {
      this.update('trigger_delay', newVal);
    },
    allow_scaling(newVal) {
      this.update('allow_scaling', newVal);
    },
  },
  created() {
    this.fetchData();
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
  margin-top: 60px;
  width: 90vw;
  margin-left: 5vw;
}

.accordion {
  box-sizing: border-box;
  display: flex;
  font-family: Arial, Helvetica, sans-serif;
  overflow: hidden;
  width: 100%;
}

.accordion-select {
  cursor: pointer;
  margin: 0;
  opacity: 0;
  z-index: 1;
}

.accordion-title {
  position: relative;
}

.accordion-title:not(:nth-last-child(2))::after {
  border: 1px solid transparent;
  bottom: 0;
  content: '';
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
}

.accordion-title span {
  bottom: 0px;
  box-sizing: border-box;
  display: block;
  position: absolute;
  white-space: nowrap;
  width: 100%;
}

.accordion-content {
  box-sizing: border-box;
  overflow: auto;
  position: relative;
  transition: margin 0.3s ease 0.1s;
}

.accordion-select:checked + .accordion-title + .accordion-content {
  margin-bottom: 0;
  margin-right: 0;
}

/* Generated styles starts here */

.accordion {
  border-color: #dedede;
  border-radius: 10px;
  border-style: solid;
  border-width: 1px;
  flex-direction: column;
  height: auto;
}

.accordion-title,
.accordion-select {
  background-color: #ffffff;
  color: #7f8787;
  width: 100%;
  height: 56px;
  font-size: 18px;
}

.accordion-select {
  margin-bottom: -56px;
  margin-right: 0;
}

.accordion-title:not(:nth-last-child(2))::after {
  border-bottom-color: rgb(234, 234, 234);
  border-right-color: transparent;
}

.accordion-select:hover + .accordion-title,
.accordion-select:checked + .accordion-title {
  background-color: #ffffff;
}

.accordion-title span {
  transform: rotate(0deg);
  -ms-writing-mode: lr-tb;
  filter: progid:DXImageTransform.Microsoft.BasicImage(rotation=0);
  padding-left: 28px;
  padding-right: 28px;
  line-height: 56px;
}

.accordion-content {
  background-color: #f7f7f7;
  color: #7f8787;
  height: 200px;
  margin-bottom: -200px;
  margin-right: 0;
  padding: 5px;
  width: 100%;
}
</style>
