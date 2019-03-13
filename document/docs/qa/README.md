# Q&A
## Uniqys KitとEasy FrameworkとEasy Clientの関係がわからない

[Uniqys Kitのドキュメント](https://uniqys.github.io/UniqysKitDocs/ja/easy-framework/easy-framework.html#%E4%BB%95%E7%B5%84%E3%81%BF)をご確認ください

このサンプルで使っている構成は、以下のようになっています

### 図
<img :src="$withBase('/img/Uniqys.png')" alt="foo">

## データを消したい
uniqys initしたディレクトリで以下を実行してください

```sh
rm -rf .data
uniqys init ./dapp.json
```
