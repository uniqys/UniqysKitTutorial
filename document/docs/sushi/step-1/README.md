# Step 1
## sushiについて
このチュートリアルでは、Uniqys Kitを使って[CryptOsushi](https://cryptosushi.samples.uniqys.net/)の簡易版(sushi)を作成していきます。

sushiアプリにおいて、各ユーザーは自分のアドレスと通貨(Gari)を保有しています。
ユーザーはおすしを握ったり、値段をつけて出品したりできます。

さらに、他のユーザーが出品したおすしを購入することが出来ます。
購入したおすしは自分のものとなり、再度値段をつけて出品ができます。

Step1ではfrontendのモックを作成します。Step2ではモックとUniqysとつなげていきます。

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

App.vueを以下のようにしてください

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

templateとscriptブロックを以下のようにします。styleは残しておいてください

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

scriptブロックを以下のようにします

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

おすしのデータは下記の要素で構成されています。

- id    ：おすしのid
- status：販売中の状態。販売中であれば`'sell'`、販売中でないなら`'normal'`
- price ：おすしの値段。単位は`Gari`。
- owner ：おすしを保有してるユーザーのアドレス
- dna   ：おすしの特徴(皿、ネタ、値段)を表す文字列。ある桁ずつ剰余を計算することで特徴を得られる。

## おすしの枠を表示してみる

templateブロックを以下のようにします

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

v-for している行にclassを当てます

#### sushi/frontend/src/App.vue
```html
<div class="sushi-box" v-for="sushi in sushiList" :key="sushi.id">
```

styleブロックを以下のようにしてください
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
templateブロックのsushi-boxクラスを以下のように書き換えてください
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
templateブロックのsushi-boxクラスを以下のように書き換えてください
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

scriptブロックのexport defaultの中にmethodsを追加してください

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

templateブロックのsushi-wrapperの上あたりを以下のように書いてください

#### sushi/frontend/src/App.vue
```html
<p>私のアドレス: {{ myAddress }}</p>
<p>{{ myGari }} Gari</p>
```

dataにmyGariを追加してください
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

ここまでで、モックにこのアプリで使用するデータを用意しました。

#### アプリで使用するデータ一覧
```json
{
  'myAddress': 自分のアドレス,
  'myGari': 自分が持っている残高
  'sushiList': [
    {
      'id'    : おすしのid,
      'status': 販売の状態(sell/normal),
      'price' : おすしの値段,
      'owner' : おすしの保有者のアドレス,
      'dna'   : おすしの特徴を表す文字列
    }
  ]
}
```

## おすしをにぎってみる（仮）
templateブロックのmyGariを表示した下あたりに `にぎる` ボタンを配置してください
#### sushi/frontend/src/App.vue
```html
<p>{{ myGari }} Gari</p>
<button @click="generate()">にぎる</button>
```

scriptブロックのmethodsの中で、generateメソッドを追加してください

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
templateブロックのsushi-boxを以下のようにしてください
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

scriptブロックのdataにpriceの配列を追加してください

scriptブロックのmethodsにsellメソッドを追加してください

```js
export default {
  data() {
    return {
      price: [],
    }
  },
  methods: {
    sell(sushi, price) {
      sushi.status = 'sell'
      sushi.price = price
    },
  }
}
```
<img width="400" :src="$withBase('/img/sushi/step-1/sell.png')" alt="foo">

## おすしを買ってみる（仮）
#### sushi/frontend/src/App.vue
templateブロックのsushi-boxの最後に、以下を追加してください
```html
<div v-if="myAddress !== sushi.owner && sushi.status === 'sell'">
  <button @click="buy(sushi)">買う！</button>
</div>
```

scriptブロックのmethodsにbuyメソッドを追加してください

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
おすしの画像は [sushi.zip](https://github.com/uniqys/UniqysKitTutorial/blob/master/sushi/step-1/frontend/public/img/sushi.zip) を利用してください

`sushi/frontend/public/img/sushi/` 以下に配置してください

画像が読み込まれなかったりした場合は、`npm run serve` をCtrl-Cで止め、もう一度実行してみてください

templateブロックの、いまcode(sushi)してるところを置き換えます
#### sushi/frontend/src/App.vue
```html
<div class="sushi-image-box">
  <img :src="`/img/sushi/dish/dish-0${code(sushi).dish}.png`" alt="">
  <img :src="`/img/sushi/syari/syari.png`" alt="">
  <img :src="`/img/sushi/neta/neta-0${code(sushi).neta}.png`" alt="">
  <img :src="`/img/sushi/spice/spice-0${code(sushi).spice}.png`" alt="">
</div>
```

styleブロックに以下を追加してください

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