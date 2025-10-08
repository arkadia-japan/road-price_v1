# 不動産評価額推定システム

物件情報から固定資産税評価額を推定するPythonアプリケーションです。

## 機能

- 建物の固定資産税評価額の推定
- 土地の固定資産税評価額の推定
- 国税庁ウェブサイトから路線価情報の取得（スクレイピング）
- 物件資料画像からのテキスト抽出（OCR）
- **OCRテキストからの自動情報抽出とフォーム自動入力**
- Streamlitによる直感的なUI

## インストール

### 1. Tesseract OCRのインストール

OCR機能を使用するには、Tesseract OCRをシステムにインストールする必要があります。

**macOS（Homebrew使用）:**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

**Windows:**
- [Tesseractインストーラー](https://github.com/UB-Mannheim/tesseract/wiki)からダウンロードしてインストール
- 日本語言語データも一緒にインストールしてください

### 2. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

## 使用方法

### コマンドラインで実行

```bash
python3 main.py
```

### Streamlit UIで実行

```bash
streamlit run app.py
```

**streamlitコマンドが見つからない場合:**
```bash
python3 -m streamlit run app.py
```

**ヘッドレスモード（初回起動時のメール入力をスキップ）:**
```bash
STREAMLIT_SERVER_HEADLESS=true python3 -m streamlit run app.py
```

アプリが起動すると、以下のURLでアクセスできます：
- ローカル: http://localhost:8501
- ネットワーク: http://192.168.0.222:8501

ブラウザが自動的に開き、UIが表示されます。

#### 使い方

1. **物件資料をアップロード（オプション）**
   - 物件概要書などの画像ファイル（JPEG/PNG）をアップロード
   - 自動的にOCRでテキストを抽出
   - 抽出されたテキストから物件情報を自動解析
   - フォームに自動入力

2. **物件情報を入力/確認**
   - 自動入力された値を確認・修正
   - または手動で全項目を入力

3. **評価額を計算**
   - 「評価額を計算」ボタンをクリック
   - 土地・建物・合計の評価額を表示

## ファイル構成

### メインモジュール
- `property_data.py` - 物件データクラス
- `valuation.py` - 評価額計算ロジック
- `scraper.py` - 国税庁ウェブサイトスクレイピング
- `ocr_utils.py` - OCR（文字認識）ユーティリティ
- `text_parser.py` - OCRテキスト解析・物件情報抽出
- `app.py` - Streamlit UIアプリ
- `main.py` - コマンドライン実行用スクリプト

### テスト・ユーティリティ
- `test_ocr.py` - OCR機能のテストスクリプト
- `test_full_pipeline.py` - OCR→パーサーの完全なパイプラインテスト
- `create_test_image.py` - テスト用物件画像生成スクリプト

## デプロイ

### 自前サーバーへのデプロイ（推奨）

**Ubuntu/Debian系サーバーでの本番運用**

#### クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/arkadia-japan/road-price_v1.git
cd road-price_v1

# 自動セットアップスクリプトを実行
sudo bash deployment/setup.sh
```

セットアップ完了後、以下のコマンドでサービスを起動：

```bash
# systemdサービスを設定
sudo cp deployment/road-price.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable road-price
sudo systemctl start road-price

# Nginxを設定
sudo cp deployment/nginx.conf /etc/nginx/sites-available/road-price
sudo nano /etc/nginx/sites-available/road-price  # ドメイン名を編集
sudo ln -s /etc/nginx/sites-available/road-price /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# ファイアウォール設定
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

**詳細な手順は [`deployment/DEPLOYMENT.md`](deployment/DEPLOYMENT.md) を参照してください。**

#### 特徴

- ✅ Nginx + Gunicorn による高速・安定運用
- ✅ PostgreSQL データベース（または SQLite）
- ✅ systemd によるプロセス管理
- ✅ Let's Encrypt による無料SSL証明書
- ✅ 完全なコントロール・カスタマイズ可能

---

### クラウドへのデプロイ（Render）

**簡単・無料で始めたい場合**

#### Flask Web版のデプロイ手順

1. **GitHubリポジトリを準備**
   - このリポジトリをGitHubにプッシュ

2. **Renderにサインアップ**
   - https://render.com にアクセス
   - GitHubアカウントで登録

3. **新しいBlueprint作成**
   - Dashboard > New > Blueprint
   - GitHubリポジトリを選択
   - `render.yaml` が自動検出される

4. **環境変数の設定**
   - `SECRET_KEY`: ランダムな文字列（自動生成される）
   - `DATABASE_URL`: PostgreSQLのURL（自動設定される）

5. **デプロイ**
   - "Apply" ボタンをクリック
   - 自動的にビルド・デプロイが開始

6. **アクセス**
   - デプロイ完了後、提供されたURLでアクセス可能
   - 例: `https://road-price-app.onrender.com`

### 注意事項（Render）

- 無料プランでは15分間アクセスがないとスリープ状態になります
- 初回アクセス時は起動に30秒程度かかります
- OCR機能はTesseractが自動インストールされます

## ファイル構成

### メインモジュール
- `property_data.py` - 物件データクラス
- `valuation.py` - 評価額計算ロジック
- `scraper.py` - 国税庁ウェブサイトスクレイピング
- `ocr_utils.py` - OCR（文字認識）ユーティリティ
- `text_parser.py` - OCRテキスト解析・物件情報抽出
- `app.py` - Streamlit UIアプリ
- `main.py` - コマンドライン実行用スクリプト

### Flask Web版
- `flask_app/` - Webアプリケーション
  - `app.py` - メインアプリケーション
  - `models.py` - データベースモデル
  - `templates/` - HTMLテンプレート
  - `static/` - 静的ファイル

### デプロイ関連
- `render.yaml` - Render デプロイ設定
- `build.sh` - ビルドスクリプト
- `.env.example` - 環境変数の例

### テスト・ユーティリティ
- `test_ocr.py` - OCR機能のテストスクリプト
- `test_full_pipeline.py` - OCR→パーサーの完全なパイプラインテスト
- `create_test_image.py` - テスト用物件画像生成スクリプト

## 注意事項

⚠️ この評価額はあくまで推定値です。実際の固定資産税評価額は、地方自治体による評価に基づきます。
