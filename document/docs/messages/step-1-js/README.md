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

実行します
```bash
# /messages/frontend

npm run serve
```

ブラウザで `http://localhost:3000/` にアクセスすると、vueの最初のページが表示されるはずです。

<img :src="$withBase('/img/messages/mes1.png')" alt="Vue default">

## まっさらなページにしてみる
`messages/frontend/src/App.vue` をきれいにします

不要なcomponentsとimportも消します

#### messages/frontend/src/App.vue
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
```html
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
これから、backendの環境構築をはじめます

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

今回はローカルで動作させるため、mDNSを停止します
#### uniqys.json
```json
"network": {
  "port": 5665,
  "address": "0.0.0.0",
  "libp2pConfig": {
    "peerDiscovery": {
      "mdns": {
        "interval": 1000,
        "broadcast": true,
        "serviceTag": "uniqys.local",
        "enabled": false
      },
      "bootstrap": {
        "interval": 5000,
        "list": [],
        "enabled": false
      }
    }
  }
}
```

これでuniqysを開発開始できます

## uniqys nodeを立ち上げてみる

Uniqys起動と同時に立ち上がるバックエンドの設定を`dapp.json` に書くことができます。

#### /messages/dapp.json
```json
  "startApp": "node backend/server.js"
```

## appサーバを実装する
これから、 `backend/server.js` にバックエンドを実装していきます

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

frontendが動いてる場合は、Ctrl-Cで終了して、以下を実行してください

```bash
# /messages/backend
cd ../
# /messages/
uniqys start
```

`http://localhost:8080/hello` にアクセスしてみましょう。helloと出力されるはずです

Gateway(8080)を経由して、app(5650)を叩いています

## フロントエンドを配信する
frontendをビルドします
```bash
# /messages/frontend

npm run build
```
これにより、 `messages/frontend/dist` に、フロントエンドのファイルが生成されます

次に、生成されたファイルをexpressで配信できるようにします

バックエンドのコードに追加するときは、 **`app.use(bodyParser())` と　`app.listen(APP_PORT, APP_HOST)` の間に記載** してください

#### messages/backend/server.js
```js
app.use('/', express.static('frontend/dist'))
```

今動いているUniqysをCtrl-Cで止め、Uniqysを再スタートしてみましょう
```bash
# /messages/

uniqys start
```

`http://localhost:8080` にアクセスすると、これまで作成してきたフロントエンドのページが確認できます

今後、フロントエンドの更新を行う場合は、frontendディレクトリで `npm run build` を行ってください


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
開発中は、フロントエンドからGatewayを叩くとき、easy-clientを利用すると便利です

利用していきましょう

```bash
# /messages/frontend/

npm install --save @uniqys/easy-client
```

#### /messages/frontend/src/App.vue
```html
<script>
import { EasyClientForBrowser } from '@uniqys/easy-client'


data() {
  return {
    // ...
    client: new EasyClientForBrowser('http://localhost:8080'),
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
</script>
```

## 動作確認する

frontendをbuildしてください

uniqysを `ctrl-c` で止め、もういちど `uniqys start` してみましょう

ブラウザからフォームを送信すると、メッセージをブロックチェーン上に書き込めていることがわかります

<img :src="$withBase('/img/messages/mes7.png')" alt="post message">

シークレットウインドウで試しに実行してみてください。ブラウザを更新すると書き換わることが確認できます

<img :src="$withBase('/img/messages/mes8.png')" alt="display posted message">

次のステップでは、複数のメッセージが書き込めるように修正してみます
