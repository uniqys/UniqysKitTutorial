# backend
## 言語の変更
`uniqys start` でアプリケーションを同時に開始することができる

`dapp.json` の `startApp` に記載されたコマンドが実行される

**javascript**
```dapp.json:json
{
  "startApp": "node backend/js/server.js"
}
```

**python**
```dapp.json:json
{
  "startApp": "python backend/python/server.py"
}
```