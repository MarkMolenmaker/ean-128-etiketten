<script>
export default {
  name: 'App',
  data () {
    return {
      message: 'Sleep Schapetiketten.pdf bestand hierheen',
      file: null,
      loading: false,
      status: 'normal'
    }
  },
  methods: {
    handleFileSelect() {
      this.$refs['input-file'].click();
    },
    handleFileUpload() {
      this.loading = true;

      const input = this.$refs['input-file'];
      this.file = input.files[0];

      const formData = new FormData();
      formData.append('file', this.file);

      fetch('/api/v1/file/upload/', {
        method: 'POST',
        body: formData
      })
          .then(response => {
            if (!response.ok) {
              this.message = 'Er is iets misgegaan, probeer het opnieuw';
              this.status = 'error';
              return null;
            } else return response.blob()
          })
          .then(result => {
            if (result !== null) {
              // Open file in new tab
              const file = new Blob([result], {type: 'application/pdf'});
              window.open(URL.createObjectURL(file))
              this.message = 'Omzetten Gelukt!';
              this.status = 'success';
            }
          })
          .catch(error => {
            this.message = 'Er is iets misgegaan, probeer het opnieuw';
            this.status = 'error';
            console.log(error)
          })
          .finally(() => this.loading = false);
    }
  }
}
</script>

<template>
  <div class="wrapper">
    <div class="drop-file-input" v-if="!loading" :class="{ error: status === 'error', success: status === 'success' }"
         @dragover="(e) => { e.preventDefault(); this.message = 'Laat los om te Uploaden'; }"
         @dragleave="(e) => { e.preventDefault(); this.message = 'Sleep Schapetiketten.pdf bestand hierheen'; }"
         @drop="(e) => { e.preventDefault(); this.file = e.dataTransfer.files[0]; handleFileUpload(); }"
    >
      <div class="image"><img src="./assets/upload.png" alt="UPLOAD"></div>
      <span class="text-title">{{ message }}</span>
      <span class="text-desc">OF</span>
      <button class="btn-primary" @click="handleFileSelect()">Bestand Openen</button>
      <input class="input-file" type="file" ref="input-file" @change="handleFileUpload()" hidden/>
    </div>
    <div class="drop-file-input" v-else>
      <div class="image"><img src="./assets/loading.png" alt="UPLOAD" class="spinner"></div>
    </div>
  </div>
</template>

<style>
html, body { margin: 0; padding: 0; height: 100%; width: 100%; }

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100%;
  background: #fff;
}

.wrapper {
  margin: 10rem 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.drop-file-input {
  display: flex;
  aspect-ratio: 1 / 1;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #fff4e5;
  color: #f79300;
  border: .25rem dashed #f79300;
  border-radius: 1rem;
  cursor: pointer;
  padding: 10rem;
  transition: all .3s ease-in-out;
}
.drop-file-input.error {
  border: .25rem dashed #f00;
  color: #f00;
  background: #fcc6c6;
}
.drop-file-input.success {
  border: .25rem dashed #5ec714;
  color: #5ec714;
  background: #dcfcc6;
}

.drop-file-input:hover {
  background: #fce5c6;
}

.drop-file-input .image img {
  width: 150px;
  height: 150px;
  object-fit: contain;

  padding: 20px;
  transition: all .3s ease-in-out;
}

.drop-file-input .text-title {
  font-size: 20px;
  font-weight: bold;
  margin-top: 20px;
}

.drop-file-input .text-desc {
  font-size: 15px;
  margin-top: 10px;
}

.drop-file-input .btn-primary {
  margin-top: 20px;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #f79300;
  color: #fff;
  cursor: pointer;
  transition: all .3s ease-in-out;
}

.drop-file-input .btn-primary:hover {
  background-color: #d27d01;
}

.drop-file-input.error .btn-primary {
  background-color: #f00;
}

.drop-file-input.success .btn-primary {
  background-color: #5ec714;
}

.drop-file-input .input-file {
  display: none;
}

.spinner {
  animation: spin 3s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
