<template>
  <div>
    <div class="slider-container">
      <div class="slider-caption">
        {{ caption.length > 0 ? caption : '' }}
        <font-awesome-icon v-if="icon.length>0" :icon="['fas', icon]"></font-awesome-icon>
      </div>
      <div class="slider-box">
        <vue-slider
            v-model="value"
            :min="min"
            :max="max"
            :interval="interval"
            v-bind="slider_options"
            @drag-end="emitValue"
            @click="emitValue"
        />
      </div>
      <div class="slider-value">
        <input v-model="value" type="number" :min="min" :max="max" :step="interval"
               @input="validateInput($event.target.value)" :key="inp_key"
               @blur="emitValue"/>
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
    'caption': {
      type: String,
      default: ''
    },
    'icon': {
      type: String,
      default: ''
    },
    'min': Number,
    'max': Number,
    'interval': Number,
    'unit': String,
    'scalingFactor': Number,
    'modelValue': Number,
  },
  emits: ['update:modelValue'],
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
      factor: parseFloat(this.scalingFactor),
      inp_key: 0,
    }
  },
  methods: {
    validateInput(input) {
      let num_input = parseFloat(input);
      if (!isNaN(num_input)) {
        if (num_input < this.min) {
          this.value = this.min;
          this.inp_key += 1; // recommended way to re-render the component
        } else if (num_input > this.max) {
          this.value = this.max;
          this.inp_key += 1;
        } else {
          this.value = input;
        }
      } else {
        this.inp_key += 1;
      }
    },
    emitValue() {
      this.$emit('update:modelValue', parseFloat(this.value) / this.factor);
    },
  },
  watch: {
    modelValue(newVal) {
      this.value = newVal * this.factor;
    }
  },
  created() {
    if (isNaN(this.factor)) {
      this.factor = 1;
    }
    this.value = this.modelValue * this.factor;
  }
}
</script>

<style scoped>
.slider-container {
  display: flex;
  flex-direction: row;
}

.slider-box {
  width: 65%;
}

.slider-caption {
  font-weight: bold;
  width: auto;
  min-width: 1em;
  line-height: 2;
  display: inline-block;
  vertical-align: middle;
  margin-right: 0.6vw;
}

.slider-value {
  font-weight: bold;
  width: auto;
  margin-left: 3%;
  line-height: 2;
  display: inline-block;
  vertical-align: middle;
  text-align: center;
}

.slider-value input {
  font-size: inherit;
  border: none;
  width: 3em;
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