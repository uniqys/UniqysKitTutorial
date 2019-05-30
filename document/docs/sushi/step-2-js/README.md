# Step 2 for javascript

## backend に Uniqys Kit を導入

`@uniqys/cli`で導入される`uniqys dev-init`を用い、`backend` ディレクトリに Uniqys Kit に必要なファイルを生成します。

```bash
# sushi/
mkdir backend
cd backend
uniqys dev-init
```

#### backend/dapp.json

`uniqys start` の実行するコマンドを node のものに変更します。

```json
"startApp": "node backend/server.js"
```

#### backend/uniqys.json

今回はローカルのみで動作するため、p2p のネットワークを形成しないようにします。

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

## 必要な npm モジュールをインストールする

sushi では下記のモジュールを用います。

- express: 軽量な Web Application Framework ライブラリ
- body-parser: 受け取ったHTTPリクエストをパースするライブラリ
- memcached: javascript から memcache を呼び出すライブラリ
- keccak: ハッシュ関数の一種 "Keccak" を使えるようにするライブラリ
- axios: async/await を用いた HTTP クライアントを提供するライブラリ

```bash
# sushi/backend/

npm init

# enter enter enter...

npm install --save express body-parser memcached keccak axios
```

## `backend/server.js` を編集する

### sushi/backend/server.js
```js
const express = require("express")
const bodyParser = require("body-parser")
const Memcached = require("memcached")

const APP_HOST = '0.0.0.0'  // backendサーバが動作するホスト名
const APP_PORT = 5650       // backendサーバが動作するポート番号
const DB_HOST = 'localhost' // inner memcachedのホスト名
const DB_PORT = 5652        // inner memcachedのポート番号

const app = express() // expressを使う準備
app.use(bodyParser())

const memcached = new Memcached(`${DB_HOST}:${DB_PORT}`) // memcached apiを使う準備

/* ここにサーバの内容を書いていく */

app.listen(APP_PORT, APP_HOST) // listenを開始する
```

## `POST '/api/generate'` を作る

sushi を生成する API を作成します。

#### sushi/backend/server.js

`app.use(bodyParser())` と `app.listen(APP_PORT, APP_HOST)` の間に書いてください。

```js
const keccak = require('keccak') // ファイルの一番上

// カウンターを増やす
async function incrCount () {
  return new Promise((resolve, reject) => {
    memcached.incr('count', 1, (err, result) => {
      if (err) return reject(err)
      if (typeof result === 'number') return resolve(result)
      memcached.set('count', 1, 0, (err) => {
        if (err) return reject(err)
        resolve(1)
      })
    })
  })
}

app.post('/api/generate', async (req, res) => {
  const sender = req.header('uniqys-sender')
  const timestamp = req.header('uniqys-timestamp')
  const blockhash = req.header('uniqys-blockhash')

  const count = await incrCount()
  const newSushi = {
    id: count,
    status: 'normal',
    price: 0,
    owner: sender,
    dna: keccak('keccak256').update(count.toString()).digest('hex'),
    timestamp: timestamp,
    blockhash: blockhash
  }

  memcached.set(`sushi:${count}`, newSushi, 0, (err) => {
    if (err) {
      res.status(400).send(err)
    }
    else {
      res.sendStatus(200)
    }
  })
})
```

## `GET /api/sushiList` を作る

存在する sushi を取得する API を作成します。

#### sushi/backend/server.js
```js
// カウンターの数字を取得する
async function getCount () {
  return new Promise((resolve, reject) => {
    memcached.get('count', (err, result) => {
      if (err) return reject(err)
      if (typeof result === 'number') return resolve(result)
      resolve(0)
    })
  })
}

// sushiオブジェクトの配列を取得する
async function getSushiList (count) {
  return new Promise((resolve, reject) => {
    if (!count) return resolve([])
    const ids = new Array(count).fill(0).map((_, i) => i + 1)
    memcached.getMulti(ids.map(id => `sushi:${id}`), (err, results) => {
      if (err) return reject(err)
      resolve(ids.map(id => results[`sushi:${id}`]))
    })
  })
}

app.get('/api/sushiList', async (_, res) => {
  const count = await getCount()
  const sushiList = await getSushiList(count)
  res.send({ sushiList });
});
```

## frontend から `/api/generate` と `/api/sushiList` を叩けるようにする

frontend で必要になる Easy Client を導入します。

```bash
# sushi/frontend/

npm install --save @uniqys/easy-client
```

## frontend から gateway を叩く

フロントエンドでさきほどインストールした Easy Client を読み込みます

#### sushi/frontend/src/App.vue

```js
import { EasyClientForBrowser } from '@uniqys/easy-client'
```

#### sushi/frontend/src/App.vue

`data` を修正します。

```js
data() {
  return {
    client: new EasyClientForBrowser('http://localhost:8080'),
    myGari: 0,
    myAddress: '',
    price: [],
    sushiList: []
  }
}
```

#### sushi/frontend/src/App.vue

ブロックチェーン上でのクライアントのアドレスを取得します。

```js
async fetchMyAddress() {
  this.myAddress = this.client.address.toString()
},
```

#### sushi/frontend/src/App.vue

さきほど作成した `/api/sushiList` から、sushi のリストを取得します。

```js
async fetchSushiList() {
  const response = await this.client.get('/api/sushiList')
  const { sushiList } = response.data
  this.sushiList = sushiList
},
```

#### sushi/frontend/src/App.vue

さきほど作成した `/api/generate` に POST することで新しい sushi を生成できるようにします。

```js
async generate() {
  await this.client.post('/api/generate', {}, { sign: true })
  this.fetchSushiList()
},
```

#### sushi/frontend/src/App.vue

ページのロード時にアドレスと sushi のリストを取得します。

```js
created() {
  this.fetchMyAddress()
  this.fetchSushiList()
},
```

## 動作確認

ここまでで sushi をにぎることができるはずなので、動かしてみましょう。
まず、フロントエンドをビルドします。

```bash
# sushi/frontend/

npm run build
```

これにより、 `sushi/frontend/dist` に、フロントエンドのファイルが生成されます。

次に、生成されたファイルを express で配信できるようにします。

#### sushi/backend/server.js
```js
app.use('/', express.static('frontend/dist'))
```

そして、`uniqys start` で起動します！

```bash
# sushi/backend/

uniqys start
```

`http://localhost:8080` にアクセスすると、これまで作成してきたフロントエンドのページが確認できます。

今後、フロントエンドの更新を行う場合は、frontend ディレクトリで `npm run build` を行ってください


## Gari を取得できるようにする

Uniqys Kit の Easy Framework が提供している非公開 API の`Inner API`を使うことで、送金などのアカウント情報の操作ができます。

ここからは、Gari の残高取得や Gari を送金する操作を backend から `Inner API` を通して行います。

#### sushi/backend/server.js

`server.js` 上部でINNER APIのホスト名、ポート番号を定義します

```js
const INNER_API_HOST = 'localhost'
const INNER_API_PORT = 5651
```

現在持っている Gari を取得する API を作成します。

#### sushi/backend/server.js
```js
const axios = require('axios') // ファイルの一番上

app.get('/api/gari', async (req, res) => {
  const { address } = req.query
  const uri = `http://${INNER_API_HOST}:${INNER_API_PORT}/accounts/${address}/balance`
  const response = await axios.get(uri)
  const balance = response.data[0]
  res.send({ balance })
})
```

#### sushi/frontend/src/App.vue

フロントエンドから Gari を取得するメソッドを生成し、ページのロード時に Gari を読み込みます。

```js
created() {
  this.fetchMyAddress()
  this.fetchMyGari()
  this.fetchSushiList()
},

async fetchMyGari() {
  const response = await this.client.get('/api/gari', { params: { address: this.myAddress } })
  const { balance } = response.data
  this.myGari = balance
},
```

## Gari をもらうボタンを作る

要求者の残高を 10000 Gari にリセットする API を作成します。

#### sushi/backend/server.js
```js
app.post('/api/tap', async (req, res) => {
  const sender = req.header('uniqys-sender')

  const uri = `http://${INNER_API_HOST}:${INNER_API_PORT}/accounts/${sender}/balance`
  await axios.put(uri, JSON.stringify([10000]), { headers: { 'Content-Type': 'application/json' } })
  res.send()
})
```

#### sushi/frontend/src/App.vue

Gari をもらうボタンおよび処理を作成します。

```html
<button @click="tap()">Gariをもらう</button>
```

```js
async tap() {
  await this.client.post('/api/tap', {}, { sign: true })
  this.fetchMyGari()
},
```

## にぎるときに Gari を減らしてみる

Gari を `sender` から `to` に送る処理を追加し、
sushi をにぎる際に `OPERATOR_ADDRESS` に対して Gari を送るよう変更します。
その際、フロントエンド側でも残高を更新するよう変更します。

#### sushi/backend/server.js

```js
const OPERATOR_ADDRESS = 'b8e6493bf64cae685095b162c4a4ee0645cde586'

async function transferGari(from, to, gari) {
  return new Promise(async (resolve) => {
    const uri = `http://${INNER_API_HOST}:${INNER_API_PORT}/accounts/${from}/transfer`
    await axios.post(uri, JSON.stringify({ to, value: parseInt(gari) }), { headers: { 'Content-Type': 'application/json' } })
    resolve()
  })
}

app.post('/api/generate', async (req, res) => {

  // ...

  await transferGari(sender, OPERATOR_ADDRESS, 100)
  
  memcached.set(`sushi:${count}`, newSushi, 0, (err) => {
    // ...
})
```


#### sushi/frontend/src/App.vue

```js
async generate() {
  await this.client.post('/api/generate', {}, { sign: true })
  this.fetchSushiList()
  this.fetchMyGari()
},
```

## 売ってみる

せっかくなので握った sushi を売ってみましょう。
API は `POST /api/sell` とします。

#### sushi/backend/server.js

```js
app.post('/api/sell', async (req, res) => {
  const { sushi, price } = req.body

  const newSushi = Object.assign({}, sushi, {
    status: 'sell',
    price: price
  })

  memcached.set(`sushi:${sushi.id}`, newSushi, 0, (err) => {
    if (err) {
      res.status(400).send(err)
    }
    else {
      res.sendStatus(200)
    }
  })
})
```

#### sushi/frontend/src/App.vue

```js
async sell(sushi, price) {
  await this.client.post('/api/sell', { sushi, price }, { sign: true })
  this.fetchSushiList()
  this.fetchMyGari()
},
```

## 買ってみる

売った sushi は買わないと腐ってしまうので買えるようにしましょう。

#### sushi/backend/server.js
```js
app.post('/api/buy', async (req, res) => {
  const sender = req.header('uniqys-sender')
  const { sushi } = req.body

  const newSushi = Object.assign({}, sushi, {
    status: 'normal',
    owner: sender,
    price: 0
  })

  await transferGari(sender, sushi.owner, sushi.price)

  await memcached.set(`sushi:${sushi.id}`, newSushi, 0, (err) => {
    if (err) {
      res.status(400).send(err)
    }
    else {
      res.sendStatus(200)
    }
  })
})
```

#### sushi/frontend/src/App.vue

```js
async buy(sushi) {
  await this.client.post('/api/buy', { sushi }, { sign: true })
  this.fetchSushiList()
  this.fetchMyGari()
},
```

## 完成！

おつかれさまでした！ さきほどと同じ手順で動作確認をしてみましょう。

```bash
# sushi/frontend/
npm run build
cd ../backend
uniqys start
```

`http://localhost:8080` にアクセスすると、 sushi をにぎれること、にぎった sushi を売り買いできることが確認できます！

## 追加課題

- にぎったとき、あたらしいおすしが後ろの方に追加されてしまい微妙です。いい感じにしてみましょう
- Gari がなくてもにぎったり購入したりができてしまいます。できないようにしてみましょう
- 他の人のおすしも販売できてしまいます。backend を修正してみましょう
- 売ってないおすしも、自分のおすしも買えてしまいます。backend を修正してみましょう
- 一回販売すると、キャンセルすることができません。キャンセルできるようにしてみましょう
