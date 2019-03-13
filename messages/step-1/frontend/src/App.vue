<template>
  <div id="app">
    <input type="text" v-model="input">
    <button @click="submit()">送信</button>
    <p>{{ message }}</p>
  </div>
</template>

<script>
import { EasyClientForBrowser } from '@uniqys/easy-client'

export default {
  name: 'app',
  data() {
    return {
      client: null,
      input: '',
      message: ''
    }
  },
  created() {
    this.client = new EasyClientForBrowser('http://localhost:3000')
    this.update()
  },
  methods: {
    update() {
      this.client.get('/api/message').then((res) => {
        const message = res.data.message;
        this.message = message
      });
    },
    submit() {
      this.client.post('/api/message', { message: this.input }, { sign: true }).then(() => {
        this.update();
      })
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
