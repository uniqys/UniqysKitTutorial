# Step 1 for javascript
## frontendの環境構築
```bash
mkdir messages
cd messages

# vue-cliのインストール
npm install -g @vue/cli # すでに入ってたら不要です
exec $SHELL -l # 必要あれば

# vueのプロジェクト作成
vue create frontend
# 全部Enterでオッケーです
```

## frontendを動かしてみる
```bash
# /messages

cd frontend
```

`package.json` を編集して、ポート番号を変更しておきます
#### /messages/frontend/package.json
```js
"scripts": {
  "serve": "vue-cli-service serve --port 3000",
  "build": "vue-cli-service build",
  "lint": "vue-cli-service lint"
},
```

実行します
```bash
# /messages/frontend

npm run serve
```

ブラウザで `http://localhost:3000/` にアクセスすると、vueの最初のページが表示されるはずです。

<img :src="$withBase('/img/messages/mes1.png')" alt="Vue default">

## まっさらなページにしてみる
`messages/frontend/src/App.vue` をきれいにします

#### /messages/frontend/src/App.vue
```html
<template>
  <div id="app">
    <p>こんにちは！</p>
  </div>
</template>
```

不要なcomponentsとimportも消します

ブラウザで確認するときれいになっているはずです。
<img :src="$withBase('/img/messages/mes2.png')" alt="Hello!">

## メッセージ送信用のフォームを設置してみる

inputとbuttonを設置します

#### /messages/frontend/src/App.vue
```html
<template>
  <div id="app">
    <input type="text">
    <button>送信</button>
  </div>
</template>
```

<img :src="$withBase('/img/messages/mes3.png')" alt="set input box & button">

## 入力した値が表示されるようにする

dataの中に変数を定義します

#### /messages/frontend/src/App.vue
```js
<script>
export default {
  name: 'app',
  data() {
    return {
      input: ''
    }
  }
}
</script>
```

フォームに入力した値がinput変数に入るようにします。ついでに下にその内容を表示するようにしてみます

#### /messages/frontend/src/App.vue
```html
<template>
  <div id="app">
    <input type="text" v-model="input">
    <button>送信</button>
    <p>{{ input }}</p>
  </div>
</template>
```

フォームに入力すると、下の文字が変わることが確認できます。

<img :src="$withBase('/img/messages/mes4.png')" alt="data binding">

## 結果を表示できるようにする
message変数に結果が入るようにしてみます

#### /messages/frontend/src/App.vue
```js
data() {
  return {
    input: '',
    message: '結果だよ'
  }
},
methods: {
  submit() {
    this.message = this.input
  }
}
```

#### /messages/frontend/src/App.vue
```html
<div id="app">
  <input type="text" v-model="input">
  <button @click="submit()">送信</button>
  <p>{{ message }}</p>
</div>
```

inputに文字を入力して送信を押してみると、messageの内容が書き換わることが確認できます。

<img :src="$withBase('/img/messages/mes5.png')" alt="before submit">
[送信]をクリックすると
<img :src="$withBase('/img/messages/mes6.png')" alt="after submit">

## backendの環境構築
<img :src="$withBase('/img/Uniqys.png')" alt="after submit">

まず、uniqysのセットアップをします

uniqys-cliのインストール
```bash
npm install -g @uniqys/cli
```

```bash
# /messages/

uniqys dev-init
ls -a # .data dapp.json uniqys.json frontend/ validatorKey.json
```

これでuniqysを開発開始できます

## uniqys nodeを立ち上げてみる

`uniqys start` で一緒にappサーバを立ち上げることができます。その設定を`dapp.json` に書くことができます。

#### /messages/dapp.json
```json
  "startApp": "node backend/server.js"
```

## appサーバを実装する
これから、 `backend/server.js` にappサーバを実装していきます

まず、backendディレクトリを作り、 `npm init` します
```bash
# /messages/

mkdir backend
cd backend
npm init
# enter, enter ...
```

expressを使ってWebサーバを実装していくので、関連パッケージをインストールします

```bash
# /messages/backend/

npm install --save express body-parser memcached
```

#### messages/backend/server.js
```js
const express = require("express")
const bodyParser = require("body-parser")
const Memcached = require("memcached")

const APP_HOST = '0.0.0.0'
const APP_PORT = 5650
const DB_HOST = 'localhost'
const DB_PORT = 5652

const app = express()
const memcached = new Memcached(`${DB_HOST}:${DB_PORT}`)

app.use(bodyParser())

app.get('/hello', async (_, res) => {
  res.send('hello');
});

app.listen(APP_PORT, APP_HOST)
```

## appサーバの動作確認する

uniqysを立ち上げてみましょう

frontendが動いてる場合は、もう一つのターミナルを起動してください

```bash
# /messages/backend
cd ../
# /messages/
uniqys start
```

`http://localhost:8080/hello` にアクセスしてみましょう。helloと出力されるはずです

Gateway(8080)を経由して、app(5650)を叩いています

## messageを書き込み/読み込みできるようにしてみる

Uniqysでは、ブロックチェーンの情報をmemcachedプロトコルで操作することができます。

#### messages/backend/server.js
```js
// ...

async function getMessage () {
  return new Promise((resolve, reject) => {
    memcached.get('message', (err, result) => {
      if (err) return reject(err)
      if (typeof result === 'string') return resolve(result)
      resolve('')
    })
  })
}

// 読み込み
app.get('/api/message', async (_, res) => {
  const message = await getMessage()
  res.send({ message });
})

// 書き込み
app.post('/api/message', async (req, res) => {
  // const sender = req.header('uniqys-sender')
  const { message } = req.body

  memcached.set(`message`, message, 0, (err) => {
    if (err) {
      res.status(400).send(err)
    }
    else {
      res.sendStatus(200)
    }
  })
})

app.listen(APP_PORT, APP_HOST)
```

`message` というキーで、メッセージを保存できるようにしてみました

## frontendとbackendをつなげる

さきほどfrontendで作成したフォームで、実際にブロックチェーンの情報を操作できるようにしてみます

## frontendの修正

CORS対策のために、proxyを設定します

`messages/frontend/vue.config.js`を作成し、以下のように設定します

#### /messages/frontend/vue.config.js
```js
module.exports = {
  devServer: {
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
      "/uniqys": {
        target: "http://localhost:8080",
        changeOrigin: true,
      }
    }
  }
};
```

開発中は、フロントエンドからGatewayを叩くとき、easy-clientを利用すると便利です

利用していきましょう

```bash
# /messages/frontend/

npm install --save @uniqys/easy-client
```

#### /messages/frontend/src/App.vue
```js
import { EasyClientForBrowser } from '@uniqys/easy-client'


data() {
  return {
    // ...
    client: new EasyClientForBrowser('http://localhost:3000'),
    // ...
  }
},
created() {
  this.fetch()
},
methods: {
  fetch() {
    this.client.get('/api/message').then((res) => {
      const message = res.data.message;
      this.message = message
    });
  },
  submit() {
    this.client.post('/api/message', { message: this.input }, { sign: true }).then(() => {
      this.fetch();
    })
  }
}
```

## 動作確認する

いちどuniqysのノードを `ctrl-c` で止め、もういちど `uniqys start` してみましょう

frontendを `ctrl-c` で止め、もういちど `npm serve` してみましょう

ブラウザからフォームを送信すると、メッセージをブロックチェーン上に書き込めていることがわかります

<img :src="$withBase('/img/messages/mes7.png')" alt="post message">

シークレットウインドウで試しに実行してみてください。ブラウザを更新すると書き換わることが確認できます

<img :src="$withBase('/img/messages/mes8.png')" alt="display posted message">

次のステップでは、複数のメッセージが書き込めるように修正してみます
