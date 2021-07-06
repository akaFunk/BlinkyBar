<template>
  <div class="app">
    <h1>BlinkyBar Settings</h1>
    <slider-input caption="Speed" v-model="speed" :min="0.1" :max="10" :interval="0.1" unit="m/s"/>
    <slider-input caption="Brightness" v-model="brightness" :min="1" :max="100" :interval="1" unit="%"/>
    <slider-input caption="Trigger delay" v-model="trigger_delay" :min="0" :max="60" :interval="1" unit="s"/>
    <toggle-switch />
    <file-uploader />
  </div>
</template>

<script>
import SliderInput from "./components/SliderInput";
import ToggleSwitch from "@/components/ToggleSwitch";
import FileUploader from "@/components/FileUploader";

export default {
  name: 'App',
  components: {
    SliderInput,
    ToggleSwitch,
    FileUploader
  },
  data: function () {
    return {
      speed: 1,
      brightness: 50,
      trigger_delay: 0,
    }
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
</style>
