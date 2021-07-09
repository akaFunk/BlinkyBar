<template>
  <div class="toggle-container">
    <div class="toggle-caption">
      <font-awesome-icon v-if="icon.length>0" :icon="['fas', icon]"></font-awesome-icon>
    </div>
    <div class="slider-value">
    <label class="switch">
      <input type="checkbox" :checked="modelValue" @change="update">
      <span class="slider round"></span>
    </label>
    {{ modelValue ? 'On' : 'Off' }}
    </div>
  </div>
</template>

<script>
export default {
  name: "ToggleSwitch",
  props: {
    caption: String,
    icon: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      'modelValue': Boolean,
    }
  },
  emits: ['update:modelValue'],
  methods: {
    update(e) {
      this.modelValue = e.target.checked;
      this.$emit('update:modelValue', this.modelValue);
    }
  }
}
</script>

<style scoped>
.toggle-container {
  display: flex;
  flex-direction: row;
}

.toggle-caption {
  font-weight: bold;
  width: auto;
  min-width: 1em;
  line-height: 2;
  display: inline-block;
  vertical-align: middle;
  margin-right: 0.6vw;
}
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 20px;
}

/* Hide default HTML checkbox */
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e1e1e1;
  -webkit-transition: .4s;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 4px;
  bottom: 3px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .slider {
  background-color: #9cd5ff;
}
input:checked:hover + .slider {
  background-color: #69c0ff;
}

input:focus + .slider {
  box-shadow: 0 0 1px #9cd5ff;
}

input:checked + .slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

.slider-value {
  font-weight: bold;
  width: auto;
  margin-left: 3px;
  line-height: 2;
  display: inline-block;
  vertical-align: middle;
}
</style>