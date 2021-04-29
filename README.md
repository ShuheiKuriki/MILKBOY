# MILKBOY
MILKBOYアプリをDjangoで再開発しherokuで公開

- 公開url : https://milkboy-core-ai.herokuapp.com/

- オリジナルリポジトリ : https://github.com/team-rejected/MILKBOY_web
## 開発環境
開発環境用の設定ファイル
```
config/settings/dev.py
```
が必要です。この情報はGithub上に公開できないため、
開発をする方には直接伝えます。

その上でpython環境を用意し、環境内で
```buildoutcfg
pip install -r requirements.txt
```
を実行。さらにルートディレクトリにて
```buildoutcfg
python manage.py runserver
```
を実行するとローカルサーバーが起動します。

## 本番環境
本番環境については個人アカウントで公開したため、
開発者以外は変更をpushできません。
