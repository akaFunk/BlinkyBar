<template>
  <div class="app">
    <h1>BlinkyBar Settings</h1>
    <slider-input caption="Speed" v-model="speed" :min="0.1" :max="10" :interval="0.1" unit="m/s"/>
    <slider-input caption="Brightness" v-model="brightness" :min="1" :max="100" :interval="1" unit="%"
                  :scaling-factor="100"/>
    <slider-input caption="Trigger delay" v-model="trigger_delay" :min="0" :max="60" :interval="1" unit="s"/>
    <toggle-switch caption="Allow scaling" v-model="allow_scaling"/>
    <file-uploader upload-url="/set_image" result-url="/get_image_scaled?fake_param=" image-hash="image_hash"/>
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
      brightness: 0.5,
      trigger_delay: 0,
      allow_scaling: true,
      image_hash: '',
      progress_status: '',
      progress_value: 0,
      progress_msg: '',
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
