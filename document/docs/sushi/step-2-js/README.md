# Step 2 for javascript
## backendディレクトリ作る
```bash
# sushi/

mkdir backend
```

## uniqys initする
```bash
# sushi/

uniqys dev-init
```

## dapp.jsonを編集する
#### sushi/dapp.json
実行されるappのコマンドを変更する
```json
"startApp": "node backend/server.js"
```

p2pのネットワークを形成しないようにする（今回はローカルで動作するため）
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

## npm init する
```bash 
# sushi

cd backend
npm init

# enter enter enter...

npm install --save express body-parser memcached
```

## `backend/server.js` を編集する

### sushi/backend/server.js
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

app.listen(APP_PORT, APP_HOST)
```

## `POST '/api/generate'` を作る
#### sushi/backend/server.js
```js
npm install --save keccak

const keccak = require('keccak')

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
    timestamp,
    blockhash
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
`app.use(bodyParser())` と `app.listen(APP_PORT, APP_HOST)` の間に書いてください

## `GET /api/sushiList` を作る
#### sushi/backend/server.js
```js
async function getCount () {
  return new Promise((resolve, reject) => {
    memcached.get('count', (err, result) => {
      if (err) return reject(err)
      if (typeof result === 'number') return resolve(result)
      resolve(0)
    })
  })
}

async function getSushiList (count) {
  return new Promise((resolve, reject) => {
    if (!count) return resolve([])
    const ids = new Array(count).fill(0).map((_, i) => i + 1) // XXX: fill(0)いる？
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

## frontendを修正してgenerateとsushiListを叩けるようにする
```bash
# sushi/frontend

npm install --save @uniqys/easy-client
```

`frontend/package.json` を修正
#### sushi/frontend/package.json
```json
"serve": "vue-cli-service serve --port 3000",
```
uniqys nodeのgatewayが8080で、vueのデフォルトポート番号とかぶるので変更します

## `frontend/vue.config.js` を作成
#### sushi/frontend/vue.config.js
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
}
```
CORS対策です

ここまでで、実際に動くことが確認できると思います

## frontendからgatewayを叩く
**ここから難しいかも**

#### sushi/frontend/src/App.vue
```js
import { EasyClientForBrowser } from '@uniqys/easy-client'
```

#### sushi/frontend/src/App.vue
```js
{
  client: new EasyClientForBrowser('http://localhost:3000'),
  myGari: 0,
  myAddress: '',
  sushiList: []
}
```
dataを修正 デフォルトはなにもなし

#### sushi/frontend/src/App.vue
```js
async fetchMyAddress() {
  this.myAddress = this.client.address.toString()
},
```
アドレスを取得

#### sushi/frontend/src/App.vue
```js
async fetchSushiList() {
  const response = await this.client.get('/api/sushiList')
  const { sushiList } = response.data
  this.sushiList = sushiList
},
```
おすしリストを取得

#### sushi/frontend/src/App.vue
```js
created() {
  this.fetchMyAddress()
  this.fetchSushiList()
},
```
ページ更新時に取得してくる

## gariを取得できるようにする
```bash
# sushi/backend

npm install --save axios
``` 

#### sushi/backend/server.js
```js
app.get('/api/gari', async (req, res) => {
  const { address } = req.query
  const uri = `http://${INNER_API_HOST}:${INNER_API_PORT}/accounts/${address}/balance`
  const response = await axios.get(uri)
  const balance = response.data[0]
  res.send({ balance })
})
```

#### sushi/frontend/src/App.vue
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

## Gariをもらうボタンを作る
#### sushi/frontend/src/App.vue
```html
<button @click="tap()">Gariをもらう</button>
```

#### sushi/frontend/src/App.vue
```js
async tap() {
  await this.client.post('/api/tap', {}, { sign: true })
  this.fetchMyGari()
},
```

#### sushi/backend/server.js
```js
app.post('/api/tap', async (req, res) => {
  const sender = req.header('uniqys-sender')

  const uri = `http://${INNER_API_HOST}:${INNER_API_PORT}/accounts/${sender}/balance`
  await axios.put(uri, JSON.stringify([10000]), { headers: { 'Content-Type': 'application/json' } })
  res.send()
})
```

## にぎるときにGariを減らしてみる

#### sushi/frontend/src/App.vue
```js
async generate() {
  await this.client.post('/api/generate', {}, { sign: true })
  this.fetchSushiList()
  this.fetchMyGari()
},
```

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
  res.send()
})
```

## 売ってみる

#### sushi/frontend/src/App.vue
```js
async sell(sushi, price) {
  await this.client.post('/api/sell', { sushi, price }, { sign: true })
  this.fetchSushiList()
  this.fetchMyGari()
},
```

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
*他の人のおすしも販売できちゃう・・*

## 買ってみる

#### sushi/frontend/src/App.vue
```js
async buy(sushi) {
  await this.client.post('/api/buy', { sushi }, { sign: true })
  this.fetchSushiList()
  this.fetchMyGari()
},
```

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

  await memcached.set(`sushi:${sushi.id}`, newSushi, 0, (err) => {
    if (err) {
      res.status(400).send(err)
    }
    else {
      res.sendStatus(200)
    }
  })
  await transferGari(sender, sushi.owner, sushi.price)
  res.send()
})
```
*売ってないおすしも、自分のおすしも買えちゃう・・*

## 完成！
お疲れ様でした！
動作を確認してみましょう。一通りのおすし操作をすることができるようになりました！

## 追加課題
- にぎったとき、あたらしいおすしが後ろの方に追加されてしまい微妙です。いい感じにしてみましょう
- Gariがなくてもにぎったり購入したりができてしまいます。できないようにしてみましょう
- 他の人のおすしも販売できてしまいます。backendを修正してみましょう
- 売ってないおすしも、自分のおすしも買えてしまいます。backendを修正してみましょう
- 一回販売すると、キャンセルすることができません。キャンセルできるようにしてみましょう