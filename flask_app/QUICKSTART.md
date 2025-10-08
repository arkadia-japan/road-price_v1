# クイックスタートガイド

不動産評価額推定システム（Flask版）をすぐに始めるためのガイドです。

## 1. セットアップ（初回のみ）

### ステップ1: 依存パッケージのインストール

```bash
cd flask_app
pip install -r requirements.txt
```

### ステップ2: データベースの初期化

```bash
python init_db.py
```

テストユーザーを作成するか聞かれたら `y` を入力してください：
- メールアドレス: `test@example.com`
- パスワード: `password123`

## 2. アプリケーションの起動

```bash
python app.py
```

または

```bash
flask run
```

サーバーが起動したら、ブラウザで以下にアクセス：
```
http://localhost:5000
```

## 3. 使ってみる

### 初めての方

1. トップページの「無料で始める」をクリック
2. メールアドレスとパスワードを入力して新規登録
3. ログイン後、「評価額を算出する」をクリック
4. 物件情報を入力して評価額を計算

### テストユーザーでログイン

1. トップページの「ログイン」をクリック
2. 以下の情報でログイン：
   - メールアドレス: `test@example.com`
   - パスワード: `password123`

## 4. 主な機能

- **ダッシュボード**: 登録した物件の一覧を確認
- **評価額算出**: 新しい物件の評価額を計算
- **物件詳細**: 評価額の内訳を確認

## トラブルシューティング

### エラー: "No module named 'flask'"

```bash
pip install Flask Flask-SQLAlchemy Flask-Login
```

### エラー: "Unable to open database file"

```bash
# データベースを再初期化
rm -rf instance/
python init_db.py
```

### ポート5000が既に使用されている

```bash
# 別のポートで起動
flask run --port 5001
```

## 次のステップ

- [README.md](README.md) - 詳細なドキュメント
- 本番環境へのデプロイ方法
- カスタマイズ方法

## お困りですか？

- app.py の 263行目あたりの `debug=True` でデバッグモードを確認
- ログを確認してエラーメッセージを探す
- データベースをリセットしてみる（`rm -rf instance/` → `python init_db.py`）
