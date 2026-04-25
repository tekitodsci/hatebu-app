# ネタ探知機 🔥

はてなブックマーク新着から「これから来る」ネタを早期検出するWebアプリ。

## ローカルで実行

```bash
pip install -r requirements.txt
python app.py
```

ブラウザで http://localhost:8080 を開いてください。

## Render にデプロイ（無料）

1. このフォルダを GitHub にプッシュ
2. [Render](https://render.com) にサインアップ
3. 「New Web Service」→ GitHub リポジトリを接続
4. 以下を設定:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. 「Create Web Service」をクリック
6. 数分でデプロイ完了、URLが発行される

## Railway にデプロイ（無料枠あり）

1. [Railway](https://railway.app) にサインアップ
2. 「New Project」→「Deploy from GitHub repo」
3. リポジトリを選択するだけで自動デプロイ

## ファイル構成

- `app.py` - Flask アプリ本体
- `requirements.txt` - 依存パッケージ
- `render.yaml` - Render 用デプロイ設定
- `README.md` - このファイル
