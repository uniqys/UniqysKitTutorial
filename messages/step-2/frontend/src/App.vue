<template>
  <div id="app">
    <input type="text" v-model="input">
    <button @click="submit()">送信</button>
    <table>
      <thead>
        <tr>
          <th>sender</th>
          <th>contents</th>
          <th>timestamp</th>
          <th>blockhash</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="message in messages" :key="message.id">
          <td>{{ message.sender }}</td>
          <td>{{ message.contents }}</td>
          <td>{{ message.timestamp }}</td>
          <td>{{ message.blockhash }}</td>
        </tr>
      </tbody>
    </table>
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
      messages: []
    }
  },
  created() {
    this.client = new EasyClientForBrowser('http://localhost:3000')
    this.update()
  },
  methods: {
    update() {
      this.client.get('/api/message').then((res) => {
        const { messages } = res.data;
        this.messages = messages
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
