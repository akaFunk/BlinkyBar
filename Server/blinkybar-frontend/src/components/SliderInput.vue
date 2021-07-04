<template>
  <div>
    <h3>{{ caption }}</h3>
    <div class="slidercontainer">
      <div class="sliderbox">
        <vue-slider
            v-model="value"
            :min="parseFloat(min)"
            :max="parseFloat(max)"
            :interval="parseFloat(interval)"
            v-bind="slider_options"
        />
      </div>
      <div class="slidervalue">
        <input v-model="value" /> {{ unit }}
      </div>
    </div>
  </div>
</template>

<script>
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/antd.css'

export default {
  name: "SliderInput",
  components: {
    VueSlider,
  },
  props: ['name', 'caption', 'min', 'max', 'interval', 'default', 'unit'],

  data() {
    return {
      slider_options: {
        dotSize: 20,
        width: 'auto',
        height: 10,
        contained: true,
        direction: 'ltr',
        data: null,
        dataLabel: 'label',
        dataValue: 'value',
        disabled: false,
        clickable: true,
        duration: 0.1,
        adsorb: false,
        lazy: false,
        tooltip: 'active',
        tooltipPlacement: 'top',
        tooltipFormatter: void 0,
        useKeyboard: false,
        keydownHook: null,
        dragOnClick: false,
        enableCross: true,
        fixed: false,
        minRange: void 0,
        maxRange: void 0,
        order: true,
        marks: false,
        dotOptions: void 0,
        dotAttrs: void 0,
        process: true,
        dotStyle: void 0,
        railStyle: void 0,
        processStyle: void 0,
        tooltipStyle: void 0,
        stepStyle: void 0,
        stepActiveStyle: void 0,
        labelStyle: void 0,
        labelActiveStyle: void 0,
      },
      value: 5,
    }
  },
}
</script>

<style scoped>
.slidercontainer {
  display: flex;
  flex-direction: row;
}
.sliderbox {
  width: 75%;
}

.slidervalue {
  font-weight: bold;
  width: auto;
  margin-left: 3%;
  line-height: 2;
  display: inline-block;
  vertical-align: middle;
}

.slidervalue input {
  font-size: inherit;
  border: none;
  width: 2em;
  font-weight: bold;
  text-align: right;
}
</style>