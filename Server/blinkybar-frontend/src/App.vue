<template>
  <div class="app">
    <h1>BlinkyBar Settings</h1>
    <slider-input caption="Speed" :default_value="1" :min="0.1" :max="10" :interval="0.1" unit="m/s"/>
    <slider-input caption="Brightness" :default_value="50" :min="1" :max="100" :interval="1" unit="%"/>
    <slider-input caption="Trigger delay" :default_value="0" :min="0" :max="60" :interval="1" unit="s"/>
    <file-uploader />
  </div>
</template>

<script>
import SliderInput from "./components/SliderInput";
import FileUploader from "@/components/FileUploader";

export default {
  name: 'App',
  components: {
    SliderInput,
    FileUploader
  },
  data: function () {
    return {
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
