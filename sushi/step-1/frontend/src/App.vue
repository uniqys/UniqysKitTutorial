<template>
  <div id="app">
    <div>
      <p>address: {{ myAddress }}</p>
      <p>{{ myGari }} Gari</p>
      <button @click="generate()">にぎる</button>
    </div>
    <div class="sushi-wrapper">
      <div class="sushi-box" v-for="sushi in sushiList" :key="sushi.id">
        <p>{{ myAddress === sushi.owner ? '私のおすし' : 'だれかのおすし' }}</p>
        <div class="sushi-image-box">
          <img :src="`/img/sushi/dish/dish-0${code(sushi).dish}.png`" alt="">
          <img :src="`/img/sushi/syari/syari.png`" alt="">
          <img :src="`/img/sushi/neta/neta-0${code(sushi).neta}.png`" alt="">
          <img :src="`/img/sushi/spice/spice-0${code(sushi).spice}.png`" alt="">
        </div>
        <p v-if="sushi.status === 'sell'">販売中</p>
        <p v-if="sushi.status === 'sell'">{{ sushi.price }} Gari</p>
        <div v-if="myAddress === sushi.owner && sushi.status === 'normal'">
          <input type="text" placeholder="販売額" v-model="price[sushi.id]">
          <button @click="sell(sushi, price[sushi.id])">売る！</button>
        </div>
        <div v-if="myAddress !== sushi.owner && sushi.status === 'sell'">
          <button @click="buy(sushi)">買う！</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'app',
  methods: {
    generate() {
      const newId = this.sushiList.length + 1
      this.myGari -= 100
      this.sushiList.unshift({
        id: newId,
        status: 'normal',
        price: 0,
        owner: this.myAddress,
        dna: Math.random().toString(36) // ランダムな文字列を生成
      })
    },
    sell(sushi, price) {
      sushi.status = 'sell'
      sushi.price = price
    },
    buy(sushi) {
      this.myGari -= sushi.price
      sushi.status = 'normal'
      sushi.price = 0
      sushi.owner = this.myAddress
    },
    code(sushi) {
      const dna = new Buffer(sushi.dna)
      return {
        dish: dna.readUInt16BE(0) % 10,
        neta: dna.readUInt16BE(4) % 10,
        spice: dna.readUInt16BE(8) % 10,
      }
    }
  },
  data() {
    return {
      myGari: 10000,
      myAddress: '0xhogehoge',
      price: [],
      sushiList: [
        { // 自分の販売中じゃないおすし
          id: 1,
          status: 'normal',
          price: 0,
          owner: '0xhogehoge',
          dna: 'irjiorgoiwegjioergj'
        },
        { // 自分の販売中のおすし
          id: 2,
          status: 'sell',
          price: 0,
          owner: '0xhogehoge',
          dna: '0rtihij6i45h4jgioijerf'
        },
        { // 他の人の販売中じゃないおすし
          id: 3,
          status: 'normal',
          price: 0,
          owner: '0xhugahuga',
          dna: 'x3igwegjsij5gjj35p4hi45h'
        },
        { // 他の人の販売中のおすし
          id: 4,
          status: 'sell',
          price: 5000,
          owner: '0xhugahuga',
          dna: 'irjiorgoiwegjioergj'
        },
      ]
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
.sushi-wrapper {
  display: flex;
  flex-wrap: wrap;
}
.sushi-box {
  width: 200px;
  height: 300px;
  margin: 8px;
  border: 1px solid black;
}
.sushi-image-box {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto;
}
.sushi-image-box img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100px;
  height: 100px;
}
</style>
