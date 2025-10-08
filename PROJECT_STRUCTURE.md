# プロジェクト構造

不動産評価額推定システムの全体構造です。

## ディレクトリ構成

```
road price_v1/
├── README.md                    # プロジェクト全体のREADME
├── PROJECT_STRUCTURE.md         # このファイル
│
├── # コアモジュール（既存）
├── property_data.py             # 物件データクラス
├── valuation.py                 # 評価額計算ロジック
├── scraper.py                   # 国税庁Webスクレイピング
├── ocr_utils.py                 # OCR（文字認識）ユーティリティ
├── text_parser.py               # OCRテキスト解析
│
├── # Streamlitアプリ（既存）
├── app.py                       # Streamlit UIアプリ
├── main.py                      # コマンドライン実行用
│
├── # テスト・ユーティリティ
├── test_ocr.py                  # OCRテスト
├── test_full_pipeline.py        # OCR→パーサーテスト
├── create_test_image.py         # テスト画像生成
├── sample_property.png          # サンプル物件画像
│
├── # 設定ファイル
├── requirements.txt             # Python依存パッケージ
│
└── # Flask Webアプリケーション（新規）
    └── flask_app/
        ├── README.md            # Flaskアプリのドキュメント
        ├── QUICKSTART.md        # クイックスタートガイド
        ├── app.py               # メインアプリケーション
        ├── models.py            # データベースモデル
        ├── init_db.py           # DB初期化スクリプト
        ├── requirements.txt     # Flask用依存パッケージ
        │
        ├── instance/            # データベースファイル（自動生成）
        │   └── app.db           # SQLiteデータベース
        │
        ├── templates/           # HTMLテンプレート
        │   ├── base.html        # ベーステンプレート
        │   ├── index.html       # トップページ
        │   ├── login.html       # ログイン
        │   ├── register.html    # 新規登録
        │   ├── dashboard.html   # ダッシュボード
        │   ├── evaluate.html    # 評価額算出
        │   └── property_detail.html  # 物件詳細
        │
        └── static/              # 静的ファイル
            ├── css/
            │   └── style.css    # カスタムスタイル
            ├── js/              # JavaScript（将来的に使用）
            └── images/          # 画像ファイル
```

## アプリケーション比較

### Streamlitアプリ（`app.py`）

**特徴:**
- プロトタイプ・デモ向け
- コードが簡潔
- 開発が高速
- インタラクティブなUI

**用途:**
- 社内ツール
- データ分析デモ
- プロトタイピング

**起動方法:**
```bash
streamlit run app.py
```

### Flask Webアプリ（`flask_app/`）

**特徴:**
- 本格的なWebアプリケーション
- ユーザー認証あり
- データベース永続化
- カスタマイズ可能

**用途:**
- 公開Webサービス
- 複数ユーザー対応
- 本番環境デプロイ

**起動方法:**
```bash
cd flask_app
python app.py
```

## 機能マトリクス

| 機能 | Streamlit | Flask |
|------|-----------|-------|
| 評価額計算 | ✓ | ✓ |
| OCR機能 | ✓ | - |
| テキスト解析 | ✓ | - |
| ユーザー登録 | - | ✓ |
| ログイン | - | ✓ |
| データ保存 | - | ✓ |
| 履歴管理 | - | ✓ |
| レスポンシブ | △ | ✓ |

## コアモジュールの利用

Flask Webアプリは、既存のコアモジュールを利用して評価額を計算します：

```python
# flask_app/app.py の evaluate ルート内
from property_data import PropertyData
from valuation import calculate_building_valuation, calculate_land_valuation

property_data = PropertyData(...)
land_value = calculate_land_valuation(property_data)
building_value = calculate_building_valuation(property_data)
```

## データフロー

### Streamlitアプリ
```
ユーザー入力/画像アップロード
    ↓
OCR処理（ocr_utils.py）
    ↓
テキスト解析（text_parser.py）
    ↓
評価額計算（valuation.py）
    ↓
結果表示
```

### Flask Webアプリ
```
ユーザー登録/ログイン
    ↓
物件情報入力
    ↓
評価額計算（valuation.py）
    ↓
データベース保存（models.py）
    ↓
結果表示・履歴管理
```

## 開発の進め方

1. **プロトタイプ段階**: Streamlitアプリで機能を試作
2. **検証段階**: コアロジックを独立モジュール化
3. **本番化**: Flaskアプリで本格的なWebサービス化

## 今後の拡張

### Streamlitアプリ
- [ ] 路線価スクレイピングの統合
- [ ] より高度なOCR処理
- [ ] データエクスポート機能

### Flask Webアプリ
- [ ] OCR機能の統合
- [ ] 路線価APIの統合
- [ ] PDF出力機能
- [ ] 物件比較機能
- [ ] ユーザープロフィール管理
- [ ] APIエンドポイント（REST API）

## 技術スタック

### 共通
- Python 3.9+
- property_data.py (データクラス)
- valuation.py (評価ロジック)

### Streamlit
- Streamlit 1.28+
- Pillow (画像処理)
- pytesseract (OCR)
- BeautifulSoup4 (スクレイピング)

### Flask
- Flask 3.0+
- Flask-SQLAlchemy (ORM)
- Flask-Login (認証)
- Bootstrap 5 (UI)
- SQLite (データベース)
