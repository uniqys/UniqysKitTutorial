# Step 2 for javascript
## 方針
先程作成したmessagesアプリに、複数のメッセージを登録できるようにしてみます

ヒント:

- メッセージの数をカウントする (key: `count`)
- メッセージを登録する (key: `messages:${id}`)
- メッセージを表示する

できそうな人は、やってみてください。いろんなやりかたで実装できると思います

*サンプルはエラー処理を省略しているので、気になる人はやってみてください*

## 複数のメッセージを書き込めるようにする

#### messages/backend/server.js
```js
// countを1つ増やしてその結果を返します
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

// countをidとしてブロックチェーンに書き込みます
app.post('/api/message', async (req, res) => {
  const sender = req.header('uniqys-sender')
  const timestamp = req.header('uniqys-timestamp')
  const blockhash = req.header('uniqys-blockhash')
  const { message } = req.body

  const count = await incrCount()

  memcached.set(`messages:${count}`, {
    id: count,
    sender,
    timestamp,
    blockhash,
    contents: message
  }, 0, (err) => {
    if (err) {
      res.status(400).send(err)
    }
    else {
      res.sendStatus(200)
    }
  })
})
```

`messages:${count}` に書き込む内容は、以下のようにしてみました
```js
{
  id: number,        // id
  sender: string,    // address
  timestamp: string, // timestamp
  blockhash: string, // blockhash
  contents: message  // message body
}
```

## 複数のメッセージを読み込めるようにする
つぎに、読み込めるようにしてみます

#### messages/backend/server.js
```js
// ブロックチェーンからメッセージの配列を取得します
async function getMessages (count) {
  return new Promise((resolve, reject) => {
    if (!count) return resolve([])
    const ids = new Array(count).fill(0).map((_, i) => i + 1) // [1, 2, ..., count]
    memcached.getMulti(ids.map(id => `messages:${id}`), (err, results) => {
      if (err) return reject(err)
      resolve(ids.map(id => results[`messages:${id}`]))
    })
  })
}

// メッセージの総数を取得します
async function getCount () {
  return new Promise((resolve, reject) => {
    memcached.get('count', (err, result) => {
      if (err) return reject(err)
      if (typeof result === 'number') return resolve(result)
      resolve(0)
    })
  })
}

// メッセージの配列を返します
app.get('/api/message', async (_, res) => {
  const count = await getCount()
  const messages = await getMessages(count)
  res.send({ messages });
});
```

## frontendで取得できるようにしてみる

#### messages/frontend/src/App.vue
```js
data() {
  return {
    // ...
    messages: []
    // ...
  }
},
```
配列を受け取れるように、messagesの構造を変えました

#### messages/frontend/src/App.vue
```js
fetch() {
  this.client.get('/api/message').then((res) => {
    const messages = res.data.messages;
    this.messages = messages
  });
},
```
`GET /api/message` が配列で帰ってくるようになったので、 `fetch()` の受け取り方を変えました

#### messages/frontend/src/App.vue
```html
<div id="app">
  <input type="text" v-model="input">
  <button @click="submit()">送信</button>
  <table>
    <thead>
      <tr>
        <th>sender</th>
        <th>contents</th>
        <th>timestamp</th>
        <th>blockhash</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="message in messages" :key="message.id">
        <td>{{ message.sender }}</td>
        <td>{{ message.contents }}</td>
        <td>{{ message.timestamp }}</td>
        <td>{{ message.blockhash }}</td>
      </tr>
    </tbody>
  </table>
</div>
```
templateを変更して、tableで表示してみました

## 動作確認

uniqys nodeを`ctrl-c`で終了させたあともう一度 `uniqys start` してください

ブラウザから確認すると、複数のメッセージが送信できるようになっているはずです

<img :src="$withBase('/img/messages/mes9.png')" alt="many messages">

シークレットウインドウから、送信してみてください。複数のsenderが確認できると思います

## 追加課題

暇すぎてしょうがない場合は、以下について挑戦してみてください

順番はないので、楽しそうなものを選んでOKです

- 見た目があまりにも寂しいので、見た目を整えてみましょう
  - bulmaとかbootstrapを使ってみるのも楽しいかもしれません
  - スマホ対応してみましょう
- 返信できるようにしてみましょう
- 複数のスレッドで書き込めるようにしてみましょう
- 名前を設定して表示できるようにしてみましょう
- **sushi** に挑戦してみましょう

