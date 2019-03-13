# Step 2 for python
# 方針
先程作成したmessagesアプリに、複数のメッセージを登録できるようにしてみます

ヒント:

- メッセージの数をカウントする (key: `count`)
- メッセージを登録する (key: `messages:${id}`)
- メッセージを表示する

できそうな人は、やってみてください。いろんなやりかたで実装できると思います

*サンプルはエラー処理を省略しているので、気になる人はやってみてください*

## Data Access Object
pymemcacheの扱いを簡単にするためにData Access Objectクラス(Dao)を定義し、コンストラクタを以下のように決めます。

#### messages/backend/server.py
```python
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
pymemcacheを利用するメソッドはこのクラスにまとめておくことで、エンコード・デコードの問題を気にしなくてよくなります。詳しくはこちらの記事をご覧ください
実録！Uniqys KitでのDApps開発記 第3回「CryptOsushiのバックエンド」 by @odan3240 https://link.medium.com/CNCty6tQPU

## 複数のメッセージを書き込めるようにする

```python
# countを1つ増やしてその結果を返します
class Dao:
    def incr_count(self):
        count = self.db.get('count')
        if count:
            return self.db.incr('count', 1)
        else:
            self.db.set('count', 1)
            return 1

# countをidとしてブロックチェーンに書き込みます
    def set_message(self, count, messages):
        self.db.set('messages:'+str(count), messages)

# POSTで受け取ったメッセージとブロックチェーン関連の情報を整形して書き込むメソッドを呼び出します
@route('/api/message', method='POST')
def post_message():
    count = dao.incr_count()
    body = request.json

    messages = {
            'sender': request.get_header('uniqys-sender'),
            'timestamp': request.get_header('uniqys-timestamp'),
            'blockhash': request.get_header('uniqys-blockhash'),
            'contents': body['message']
    }

    dao.set_message(count, messages)
```

`messages:${count}` に書き込む内容は、以下のようにしてみました
```python
{
    'sender': request.get_header('uniqys-sender'), # address
    'timestamp': request.get_header('uniqys-timestamp'), # timestamp
    'blockhash': request.get_header('uniqys-blockhash'), # blockhash
    'contents': body['message'] # message body
}
```
## 複数のメッセージを読み込めるようにする
つぎに、読み込めるようにしてみます

```python
class Dao:
#  ブロックチェーンからメッセージの配列を取得します
    def get_messages(self, count):
        ids = range(1, count+1)
        result = self.db.get_multi([f'messages:{id}' for id in ids])
        return [{'id': id, **result[f'messages:{id}']} for id in ids]

# メッセージの総数を取得します
    def get_count(self):
        count = self.db.get('count')
        return int(count) if count else 0

# メッセージの配列を返します
@route('/api/message')
def get_message():
    count = dao.get_count()
    messages = dao.get_messages(count)
    return {'messages': messages}
```

## frontendで取得できるようにしてみる

dataのmessagesの構造を変えます
```js
data() {
  return {
    messages: []
  }
},
```

配列を受け取れるように、messagesの構造を変えました

#### messages/frontend/src/App.vue
```js
update() {
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
