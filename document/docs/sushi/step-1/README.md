# Step 1
# 準備
frontendディレクトリを作成します

vue-cliがインストールされていない場合はインストールしてください
```bash
# /

npm install -g @vue/cli # すでに入ってたら不要です
exec $SHELL -l # 必要あれば
```

vueが動くか確認してみます
```bash
# /

mkdir sushi
cd sushi
vue create frontend # ぜんぶEnterでオッケーです
cd frontend
npm run serve
```

ブラウザで `http://localhost:8080/` にアクセスすると、vueの最初のページが表示されるはずです。

<img width="400" :src="$withBase('/img/sushi/step-1/setup-vue.png')" alt="foo">

# おすしのモックを作っていく

## まっさらなページにしてみる
`frontend/src/App.vue` をきれいにします

不要なcomponentsとimportも消します

#### sushi/frontend/src/App.vue
```html
<template>
  <div id="app">
    <p>こんにちは！</p>
  </div>
</template>

<script>
export default {
  name: 'app'
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
```

`npm run serve` はファイルの変更を監視して自動的に表示を更新してくれます。変更を保存してブラウザで確認すると、きれいになっているはずです。

<img width="400" :src="$withBase('/img/sushi/step-1/clean-vue.png')" alt="foo">

## 自分のアドレスを作ってみる

#### sushi/frontend/src/App.vue
```html
<template>
  <div id="app">
    <p>私のアドレス: {{ myAddress }}</p>
    <p>こんにちは！</p>
  </div>
</template>

<script>
export default {
  name: 'app',
  data() {
    return {
      myAddress: '0xhogehoge',
    }
  }
}
</script>
```

<img width="400" :src="$withBase('/img/sushi/step-1/address-vue.png')" alt="foo">

## おすしのデータを作ってみる

#### sushi/frontend/src/App.vue
```html
<script>
export default {
  name: 'app',
  data() {
    return {
      myAddress: '0xhogehoge',
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
```

## おすしの枠を表示してみる

#### sushi/frontend/src/App.vue
```html
<template>
  <div id="app">
    <p>私のアドレス: {{ myAddress }}</p>
    <div class="sushi-wrapper">
      <div v-for="sushi in sushiList" :key="sushi.id">
        <p>{{ sushi.status }}</p>
        <p>{{ sushi.price }}</p>
        <p>{{ sushi.owner }}</p>
        <p>{{ sushi.dna }}</p>
      </div>
    </div>
  </div>
</template>
```

<img width="400" :src="$withBase('/img/sushi/step-1/sushi-box.png')" alt="foo">

## styleを当ててみる
#### sushi/frontend/src/App.vue
```html
<div class="sushi-box" v-for="sushi in sushiList" :key="sushi.id">
```

#### sushi/frontend/src/App.vue
```html
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
  flex-wrap: wrap;
  display: flex;
}
.sushi-box {
  width: 200px;
  height: 300px;
  margin: 8px;
  border: 1px solid black;
}
</style>
```

<img width="400" :src="$withBase('/img/sushi/step-1/sushi-style.png')" alt="foo">

## 表示を整えてみる
#### sushi/frontend/src/App.vue
```html
<div class="sushi-box" v-for="sushi in sushiList" :key="sushi.id">
  <p>{{ myAddress === sushi.owner ? '私のおすし' : 'だれかのおすし' }}</p>
  <p>{{ sushi.dna }}</p>
  <p v-if="sushi.status === 'sell'">販売中</p>
  <p v-if="sushi.status === 'sell'">{{ sushi.price }} Gari</p>
</div>
```
<img width="400" :src="$withBase('/img/sushi/step-1/display-sushi.png')" alt="foo">

## DNAからおすしの表示パターンを計算してみる
#### sushi/frontend/src/App.vue
```html
<div class="sushi-box" v-for="sushi in sushiList" :key="sushi.id">
  <p>{{ myAddress === sushi.owner ? '私のおすし' : 'だれかのおすし' }}</p>
  <p>{{ code(sushi) }}</p>
  <p v-if="sushi.status === 'sell'">販売中</p>
  <p v-if="sushi.status === 'sell'">{{ sushi.price }} Gari</p>
</div>
```

#### sushi/frontend/src/App.vue
```js
export default {
  methods: {
    code(sushi) {
      const dna = new Buffer(sushi.dna)
      return {
        dish: dna.readUInt16BE(0) % 10,
        neta: dna.readUInt16BE(4) % 10,
        spice: dna.readUInt16BE(8) % 10,
      }
    }
  },
}
```
<img width="400" :src="$withBase('/img/sushi/step-1/sushi-dna.png')" alt="foo">

## Gariの概念を導入していく
#### sushi/frontend/src/App.vue
```html
<p>私のアドレス: {{ myAddress }}</p>
<p>{{ myGari }} Gari</p>
```
#### sushi/frontend/src/App.vue
```js
data() {
  return {
    // ...
    myGari: 10000,
    // ...
  }
}
```
<img width="400" :src="$withBase('/img/sushi/step-1/gari.png')" alt="foo">

## おすしをにぎってみる（仮）
#### sushi/frontend/src/App.vue
```html
<p>{{ myGari }} Gari</p>
<button @click="generate()">にぎる</button>
```

#### sushi/frontend/src/App.vue
```js
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
}
```
<img width="400" :src="$withBase('/img/sushi/step-1/generate.png')" alt="foo">

## おすしを売ってみる（仮）
#### sushi/frontend/src/App.vue
```html
<div class="sushi-box" v-for="sushi in sushiList" :key="sushi.id">
  <p>{{ myAddress === sushi.owner ? '私のおすし' : 'だれかのおすし' }}</p>
  <p>{{ code(sushi) }}</p>
  <p v-if="sushi.status === 'sell'">販売中</p>
  <p v-if="sushi.status === 'sell'">{{ sushi.price }} Gari</p>
  <div v-if="myAddress === sushi.owner && sushi.status === 'normal'">
    <input type="text" placeholder="販売額" v-model="price[sushi.id]">
    <button @click="sell(sushi, price[sushi.id])">売る！</button>
  </div>
</div>
```

#### sushi/frontend/src/App.vue
```js
data() {
  return {
    price: [],
  }
}
methods: {
  sell(sushi, price) {
    sushi.status = 'sell'
    sushi.price = price
  },
}
```
<img width="400" :src="$withBase('/img/sushi/step-1/sell.png')" alt="foo">

## おすしを買ってみる（仮）
#### sushi/frontend/src/App.vue
```html
<div v-if="myAddress !== sushi.owner && sushi.status === 'sell'">
  <button @click="buy(sushi)">買う！</button>
</div>
```

#### sushi/frontend/src/App.vue
```js
methods: {
  buy(sushi) {
    this.myGari -= sushi.price
    sushi.status = 'normal'
    sushi.price = 0
    sushi.owner = this.myAddress
  },
}
```
<img width="400" :src="$withBase('/img/sushi/step-1/buy.png')" alt="foo">

## おすし画像を作ってみる
おすしの画像は [sushi.zip](https://github.com/nanotumblr/UniqysKitSample/blob/master/sushi/step-1/frontend/public/img/sushi.zip) を利用してください

`sushi/frontend/public/img/sushi/` 以下に配置してください

画像が読み込まれなかったりした場合は、`npm run serve` をCtrl-Cで止め、もう一度実行してみてください

いまcode(sushi)してるところを置き換えます
#### sushi/frontend/src/App.vue
```html
<div class="sushi-image-box">
  <img :src="`/img/sushi/dish/dish-0${code(sushi).dish}.png`" alt="">
  <img :src="`/img/sushi/syari/syari.png`" alt="">
  <img :src="`/img/sushi/neta/neta-0${code(sushi).neta}.png`" alt="">
  <img :src="`/img/sushi/spice/spice-0${code(sushi).spice}.png`" alt="">
</div>
```

#### sushi/frontend/src/App.vue
```css
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
```
<img width="400" :src="$withBase('/img/sushi/step-1/sushi-image.png')" alt="foo">

## モックは完成！

フロントエンドのモックが完成しました。Step 2ではUniqysとつなげていきます！