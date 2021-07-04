<template>
  <div>
    <h3>{{ caption }}</h3>
    <div class="slidercontainer">
      <div class="sliderbox">
        <vue-slider
            v-model="value"
            :min="min"
            :max="max"
            :interval="interval"
            v-bind="slider_options"
        />
      </div>
      <div class="slidervalue">
        <input :value="value" type="number" :min="min" :max="max" :step="interval"
               @input="validateInput($event.target.value)" :key="inp_key"/>
        {{ unit }}
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
  props: {
    'name': String,
    'caption': String,
    'min': Number,
    'max': Number,
    'interval': Number,
    'default_value': Number,
    'unit': String
  },
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
      value: 0,
      inp_key: 0,
    }
  },
  created() {
    this.value = this.default_value;
  },
  methods: {
    validateInput(input) {
      let num_input = parseFloat(input);
      if (!isNaN(num_input)) {
        if (num_input < this.min) {
          this.value = this.min;
        } else if (num_input > this.max) {
          this.value = this.max;
        } else {
          this.value = input
        }
      } else {
        this.inp_key += 1; // recommended way to rerender the component
      }
    }
  }
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

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
input[type=number] {
  -moz-appearance: textfield;
}
</style>