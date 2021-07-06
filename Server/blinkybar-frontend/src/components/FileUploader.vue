<template>
  <div class="fileuplaoder-box">
    <div>
      <img :src="resultUrl + imageHash" :key="imageHash" alt="scaled image stored on device"/>
    </div>
    <div>
      <input type="file" style="display: none;" ref="file" accept="image/*" @change="onFileChange">
      <button class="upload-btn" @click="$refs.file.click()">Upload new image</button>
    </div>
  </div>
</template>

<script>

export default {
  name: "FileUploader",
  props: ['uploadUrl', 'resultUrl', 'imageHash'],
  data() {
    return {
    }
  },
  methods: {
    onFileChange(e) {
      console.log(e.target.files[0].name);
      let image = e.target.files[0];
      let formData = new FormData();
      formData.append("image_obj", image);
      fetch(this.uploadUrl, {method: "PUT", body: formData});
    }
  }
}
</script>

<style scoped>
.fileuplaoder-box {
  margin-top: 1vh;
}

.upload-btn {
  background-color: #9cd5ff;
  border-radius: 3px;
  border: 1px solid #0b0e07;
  display: inline-block;
  cursor: pointer;
  color: #000000;
  font-size: 15px;
  padding: 9px 23px;
  text-decoration: none;
  text-shadow: 0 1px 0 #cddeff;
}

.upload-btn:hover {
  background-color: #69c1ff;
}

.upload-btn:active {
  position: relative;
  top: 1px;
}
</style>