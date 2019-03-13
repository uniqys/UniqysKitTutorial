# Step 2 for python
## backendディレクトリ作る
```bash
# sushi/
mkdir backend
mkdir backend/python
```

## uniqys initする
```bash
# sushi/
cd backend
uniqys dev-init
```

## dapp.jsonを編集する
#### sushi/dapp.json
実行されるappのコマンドを変更する
```json
"startApp": "python backend/server.py"
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

## 必要なpythonライブラリをインストールする
```sh
cd python
pip install bottle pymemcache requests
```

## `backend/python/server.py` を編集する
memcacheに関わる部分はmessagesと同様にDaoクラスの中で扱う

#### sushi/backend/server.py
```python
import json
import hashlib
import requests
from bottle import route, run, request, response, static_file, hook
from pymemcache.client import Client

DB_HOST = 'localhost'
DB_PORT = 5652
APP_HOST = 'localhost'
APP_PORT = 5650
INNER_API_HOST = 'localhost'
INNER_API_PORT = 5651
OPERATOR_ADDRESS = 'b8e6493bf64cae685095b162c4a4ee0645cde586'

class Dao:
    def __init__(self, host, port):
        self.db = Client(
            (host, port),
            default_noreply=False,
            serializer=self.__json_serializer,
            deserializer=self.__json_deserializer
        )

    def __json_serializer(self, key, value):
        if type(value) == str:
            return value, 1
        return json.dumps(value), 2

    def __json_deserializer(self, key, value, flags):
        if flags == 1:
            return value.decode('utf-8')
        if flags == 2:
            return json.loads(value.decode('utf-8'))
        raise Exception('Unknown serialization format')
```

## `POST '/api/generate'` を作る
#### sushi/backend/server.py
```python
class Dao:
    def incr_count(self):
        count = self.db.get('count')
        if count:
            return self.db.incr('count', 1)
        else:
            self.db.set('count', 1)
            return 1

dao = Dao(DB_HOST, DB_PORT)

@route('/api/generate', method='POST')
def post_sushi():
    count = dao.incr_count()
    keccak_hash = hashlib.sha3_256()
    keccak_hash.update(str(count).encode('utf-8'))
    owner = request.get_header('uniqys-sender')
    dna = keccak_hash.hexdigest()

    sushi = {
            'id': count,
            'status': 'normal',
            'price': 0,
            'owner': owner,
            'dna': dna,
            'timestamp': request.get_header('uniqys-timestamp'),
            'blockhash': request.get_header('uniqys-blockhash')
    }
    dao.set_sushi(sushi)

    transfer_gari(owner, OPERATOR_ADDRESS, 100)

    return 0

run(host=APP_HOST, port=APP_PORT, debug=True, reloader=True)
```

## `GET /api/sushiList` を作る
#### sushi/backend/server.py
```python
class Dao:
    def get_count(self):
        count = self.db.get('count')
        return int(count) if count else 0

    def get_sushi_list(self, count):
        ids = range(1, count+1)
        result = self.db.get_multi([f'sushi:{id}' for id in ids])
        return [{'id': id, **result[f'sushi:{id}']} for id in ids]

@route('/api/sushiList')
def get_sushi_list():
    count = dao.get_count()
    sushi_list = dao.get_sushi_list(count)
    return {'sushiList': sushi_list}
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
**こっから難しいかも**

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

#### sushi/backend/server.py
```python
@route('/api/gari')
def get_gari():
    address = request.query.address
    uri = 'http://'+INNER_API_HOST+':'+str(INNER_API_PORT)+'/accounts/'+str(address)+'/balance'
    response = requests.get(uri)
    balance = response.json()[0]
    return {'balance': balance}
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

#### sushi/backend/server.py
```python
@route('/api/tap', method='POST')
def tap_gari():
    sender = request.get_header('uniqys-sender')
    uri = 'http://'+INNER_API_HOST+':'+str(INNER_API_PORT)+'/accounts/'+str(sender)+'/balance'
    response = requests.put(uri, data=json.dumps([10000]), headers={'Content-Type': 'application/json'})
    return 0
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

#### sushi/backend/server.py
```python
def transfer_gari(sender, to, value):
    uri = 'http://'+INNER_API_HOST+':'+str(INNER_API_PORT)+'/accounts/'+str(sender)+'/transfer'
    response = requests.post(
        uri,
        data=json.dumps(dict({'to': str(to), 'value': int(value)})),
        headers={'Content-Type': 'application/json'})

@route('/api/generate', method='POST')
def post_sushi():

    # ここにお寿司を書き込む部分

    transfer_gari(owner, OPERATOR_ADDRESS, 100)

    return 0
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

#### sushi/backend/server.py
```python
@route('/api/sell', method='POST')
def sell_sushi():
    data = request.json
    sushi = data['sushi']
    price = data['price']

    new_sushi = sushi
    new_sushi['status'] = 'sell'
    new_sushi['price'] = price

    dao.set_sushi(new_sushi)
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

#### sushi/backend/server.py
```python
@route('/api/buy', method='POST')
def buy_sushi():
    sender = request.get_header('uniqys-sender')

    data = request.json
    sushi = data['sushi']
    seller = sushi['owner']
    price = int(sushi['price'])

    new_sushi = sushi
    new_sushi['status'] = 'normal'
    new_sushi['price'] = 0
    new_sushi['owner'] = sender

    dao.set_sushi(new_sushi)

    transfer_gari(sender, seller, price)

    return 0
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