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

## 注意事項

⚠️ この評価額はあくまで推定値です。実際の固定資産税評価額は、地方自治体による評価に基づきます。
