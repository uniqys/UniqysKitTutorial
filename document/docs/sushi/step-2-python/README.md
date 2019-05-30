# Step 2 for python

## backend に Uniqys Kit を導入

`@uniqys/cli`で導入される`uniqys dev-init`を用い、`backend` ディレクトリに Uniqys Kit に必要なファイルを生成します。

```bash
# sushi/
mkdir backend
cd backend
uniqys dev-init
```

#### backend/dapp.json

`uniqys start` の実行するコマンドを python のものに変更します。

```json
"startApp": "python server.py"
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

## 必要な python ライブラリをインストールする

sushi では下記のライブラリを用います。

- bottle: 軽量な Web Application Framework ライブラリ
- pymemcache: python から memcache を呼び出すライブラリ
- requests: HTTP Request を扱いやすくするライブラリ

```bash
# sushi/backend/
pip install bottle pymemcache requests
```

## `backend/server.py` を編集する

memcache に関わる部分は messages と同様に Dao クラスの中で扱います。

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

sushi を生成する API を作成します。

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

    def set_sushi(self, sushi):
        self.db.set('sushi:'+str(sushi['id']), sushi)

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

    return 0

run(host=APP_HOST, port=APP_PORT, debug=True, reloader=True)
```

## `GET /api/sushiList` を作る

存在する sushi を取得する API を作成します。

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

## frontend から `/api/generate` と `/api/sushiList` を叩けるようにする

frontend で必要になる Easy Client を導入します。

```bash
# sushi/frontend/

npm install --save @uniqys/easy-client
```

uniqys node の gateway と `vue-cli-service` がデフォルトではどちらもポート 8080 を使用するため、vue で使用するポートを `frontend/package.json` で変更します。

#### sushi/frontend/package.json

```json
"serve": "vue-cli-service serve --port 3000",
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

次に、生成されたファイルを bottle で配信できるようにします。

#### sushi/backend/server.py

```python
@route('/')
def index():
    return static_file('index.html', root='../frontend/dist')

@route('/<path:path>')
def file_path(path):
    return static_file(path, root='../frontend/dist')
```

そして、`uniqys start` で起動します！

```bash
# sushi/backend/

uniqys start
```

`http://localhost:8080` にアクセスすると、これまで作成してきたフロントエンドのページが確認できます。

今後、フロントエンドの更新を行う場合は、frontend ディレクトリで `npm run build` を行ってください

**ただし、 `npm run build` するときは python 2 系、`uniqys start` するときは python 3 系を使用してください。**

## Gari を取得できるようにする

Uniqys Kit の Easy Framework が提供している非公開 API の`Inner API`を使うことで、送金などのアカウント情報の操作ができます。

ここからは、Gari の残高取得や Gari を送金する操作を backend から `Inner API` を通して行います。

#### sushi/backend/server.py

現在持っている Gari を取得する API を作成します。

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

#### sushi/backend/server.py

```python
@route('/api/tap', method='POST')
def tap_gari():
    sender = request.get_header('uniqys-sender')
    uri = 'http://'+INNER_API_HOST+':'+str(INNER_API_PORT)+'/accounts/'+str(sender)+'/balance'
    response = requests.put(uri, data=json.dumps([10000]), headers={'Content-Type': 'application/json'})
    return 0
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
