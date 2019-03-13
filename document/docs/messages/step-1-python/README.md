# Step 1 for python
## frontendの環境構築
```sh
mkdir messages
cd messages

# vue-cliのインストール
npm install -g @vue/cli # すでに入ってたら不要です
exec $SHELL -l # 必要あれば

# vueのプロジェクト作成
vue create frontend
# 全部Enterでオッケーです
```

### frontendを動かしてみる
```bash
# /messages

cd frontend
```

`package.json` を編集して、ポート番号を変更しておきます
#### /messages/frontend/package.json
```js
"serve": "vue-cli-service serve --port 3000",
```

実行します
```bash
# /messages/frontend

npm run serve
```

ブラウザで `http://localhost:8080/` にアクセスすると、vueの最初のページが表示されるはずです。

<img :src="$withBase('/img/messages/mes1.png')" alt="Vue default">

### まっさらなページにしてみる
`frontend/src/App.vue` をきれいにします

#### /messages/frontend/src/App.vue
```html
<template>
  <div id="app">
    <p>あああ</p>
  </div>
</template>
```

不要なcomponentsとimportも消します

ブラウザで確認するときれいになっているはずです。
<img :src="$withBase('/img/messages/mes2.png')" alt="Hello!">

### メッセージ送信用のフォームを設置してみる

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


### 入力した値が表示されるようにする

dataの中に変数を定義します

#### /messages/frontend/src/App.vue
```js
// ...
export default {
  name: 'app',
  data() {
    return {
      input: ''
    }
  },
  // ...
}
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

### 結果を表示できるようにする
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
https://cdn-images-1.medium.com/max/2600/1*kRWJUnGUh-txwPFZMKkWig.png

まず、uniqysのセットアップをします

uniqys-cliのインストール
```
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
}
  "startApp": "python backend/server.py"
}
```

## appサーバを実装する
これから、 `backend/server.py` にappサーバを実装していきます

まず、backendディレクトリを作ります
```bash
mkdir backend
cd backend
```

bottleを使ってWebサーバを実装するのでpipでインストールします
またデータをmemcachedプロトコルで管理するのでpymemcacheもインストールします

```bash
# backend/
pip install bottle pymemcache
```

#### messages/backend/server.py
```python
from bottle import route, run, request, response, static_file, hook
from pymemcache.client import Client

DB_HOST = 'localhost'
DB_PORT = 5652
APP_HOST = 'localhost'
APP_PORT = 5650

@route('/')
def hello():
    return 'hello'

run(host=APP_HOST, port=APP_PORT)
```

## appサーバの動作確認する

uniqysを立ち上げてみましょう
```bash
# /messages/
uniqys start
```

`http://localhost:8080/hello` にアクセスしてみましょう。helloと出力されるはずです

Gateway(8080)を経由して、app(5650)を叩いています

## messageを書き込み/読み込みできるようにしてみる

Uniqysでは、ブロックチェーンの情報をmemcachedプロトコルで操作することができます。

#### messages/backend/server.py
```python
import json

db = Client((DB_HOST, DB_PORT))

# 読み込み
@route('/api/message')
def get_message():
    message = db.get('message')
    if message is not None:
        decoded = message.decode('utf8')
        return {'message': decoded}
    response.status = 400

# 書き込み
@route('/api/message', method='POST')
def post_message():
    sender = request.get_header('uniqys-sender')
    body = request.json
    message = body['message']
    db.set('message', message.encode('utf8'))
```

`message` というキーで、メッセージを保存できるようにしてみました
frontendからはJSONの形でメッセージが渡されるためjsonモジュールを使っています。
また、pymemcacheで書き込む前にUTF-8でエンコードし、読み込むときは逆にデコードしています。

# frontendとbackendをつなげる

さきほどfrontendで作成したフォームで、実際にブロックチェーンの情報を操作できるようにしてみます

## frontendの修正

CORS対策のために、proxyを設定します

`frontend/vue.config.js`を作成し、以下のように設定します

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
    client: new EasyClientForBrowser('http://localhost:3000'),
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

シークレットウインド胃で試しに実行してみてください。ブラウザを更新すると書き換わることが確認できます

<img :src="$withBase('/img/messages/mes8.png')" alt="display posted message">

次のステップでは、複数のメッセージが書き込めるように修正してみます
