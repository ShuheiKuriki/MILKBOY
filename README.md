# MILKBOY
M1王者ミルクボーイ風AI漫才アプリ「無限ミルクボーイ」

お題を与えるとWikipediaから適切な情報を抜き出してきて自動でネタを作り、音声読み上げしてくれます。
お題をノンジャンルでランダムに生成したり、ジャンルを指定してネタを作ることも可能。

定期的にネタをツイートするtwitter botもあり。

- 公開url : https://www.milkboy-core-ai.tech/
- twitter bot : https://twitter.com/milkboy_core_ai

## 開発経緯
Yahoo!Japanハッカソン　HackDay2021　https://hackday.jp/　にて、4人でチーム開発し2日間でとりあえず動くだけのプロトタイプを作成
https://github.com/team-rejected/MILKBOY_web がオリジナル

その後、個人開発にて
- アルゴリズム改善・ひたすらバグ修正
- デザイン
- 機能追加（ランダムモード、ジャンルモード、デモモードなど）
- twitter bot開発
を行う。

##使用技術
主要言語 : Python, javascript
Webフレームワーク : Django
JSライブラリ : なし
データベース : なし
デザイン : Bootstrap(デザインテンプレート使用)
デプロイ先 : heroku
その他 : Twiiter API, Wikipediaスクレイピング, 自然言語処理


## 開発環境
開発環境用の設定ファイル
```
config/settings/dev.py
```
が必要です。この情報はGithub上に公開できないため、
開発をする際には直接伝えます。

その上でpython環境を用意し、環境内で
```buildoutcfg
pip install -r requirements.txt
```
を実行。さらにルートディレクトリにて
```buildoutcfg
python manage.py runserver
```
を実行するとローカルサーバーが起動します。

本番環境については個人アカウントで公開してしまったため、
自分以外は変更をpushできないと思われます(loginする必要があるので)。
