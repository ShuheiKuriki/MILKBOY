# MILKBOY
MILKBOYアプリをDjangoで再開発しherokuで公開

- 公開url : https://milkboy-core-ai.herokuapp.com/ →2024/2/19現在閉鎖済

- オリジナルリポジトリ : https://github.com/team-rejected/MILKBOY_web

M1王者ミルクボーイ風AI漫才アプリ「無限ミルクボーイ」

お題を与えるとWikipediaから適切な情報を抜き出してきて自動でネタを作り、音声読み上げしてくれます。
お題をノンジャンルでランダムに生成したり、ジャンルを指定してネタを作ることも可能。

定期的にネタをツイートするTwitter botもあり。

- 公開url : https://www.milkboy-core-ai.tech/ →2024/2/19現在閉鎖済
- Twitter bot : https://twitter.com/milkboy_core_ai →2024/2/19現在ツイートは停止していますが、過去のツイートは残っています。

## 開発経緯
Yahoo!JapanハッカソンHackDay2021
https://hackday.jp/　
にて、4人でチーム開発し2日間でとりあえず動くだけのプロトタイプを作成
(https://github.com/team-rejected/MILKBOY_web がオリジナル)

その後、個人開発にて

- アルゴリズム改善・ひたすらバグ修正
- デザイン
- 機能追加（ランダムモード、ジャンルモード、デモモードなど）
- twitter bot開発

を行い公開。開発期間は2,3週間ほど。

## 使用技術
- 主要言語 : Python, javascript
- Webフレームワーク : Django
- JSライブラリ : なし
- データベース : なし
- デザイン : Bootstrap(デザインテンプレート使用)
- デプロイ先 : heroku
- その他 : Twiiter API, Wikipediaスクレイピング, 自然言語処理


## 開発環境
開発環境用の設定ファイル
```
config/settings/dev.py
```
が必要です。この情報はGithub上に公開できないため、
開発をする方には直接伝えます。

その上でpython環境を用意し、環境内で
```commandline
pip install -r requirements.txt
```
を実行。さらにルートディレクトリにて
```commandline
python manage.py runserver
```
を実行するとローカルサーバーが起動します。

## 本番環境
本番環境については個人アカウントで公開したため、
開発者以外は変更をpushできません。
```commandline
git push origin master
```
を実行すると、herokuにも自動的にpushされます。
