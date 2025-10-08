# 不動産評価額推定システム - Flask Webアプリケーション

物件情報から固定資産税評価額を推定する本格的なWebアプリケーションです。マジックリンク認証、OCR機能、評価履歴管理などを備えています。

## 機能

### 認証機能
- **マジックリンク認証**: パスワード不要のメールリンクでログイン
- **通常のログイン/登録**: メールアドレスとパスワードでのログイン
- **ユーザー管理**: Flask-Loginによるセッション管理

### 評価ツール
- **ファイルアップロード**: 固定資産登録事項証明書の画像をアップロード
- **OCR自動抽出**: Tesseract OCRで画像から物件情報を自動抽出
- **手動入力**: フォームから直接入力
- **非同期計算**: JSON APIによる評価額計算
- **リアルタイム結果表示**: ローディングスピナーと結果表示

### 履歴管理
- **評価履歴保存**: 計算結果を自動保存
- **履歴一覧**: 過去の評価結果を閲覧
- **ページネーション**: 大量の履歴を効率的に表示
- **統計情報**: 総評価回数、平均評価額、最高評価額の表示

### UI/UX
- **レスポンシブデザイン**: Bootstrap 5でモバイル対応
- **直感的なUI**: タブ切り替え、ドラッグ&ドロップ
- **エラーハンドリング**: ユーザーフレンドリーなエラーメッセージ

## 技術スタック

- **Webフレームワーク**: Flask 3.0+
- **データベース**: SQLite (SQLAlchemy ORM)
- **認証**: Flask-Login
- **フロントエンド**: Bootstrap 5, Bootstrap Icons, JavaScript (Fetch API)
- **セキュリティ**: Werkzeug (パスワードハッシュ化)
- **OCR**: Tesseract OCR, pytesseract
- **画像処理**: Pillow

## ディレクトリ構造

```
flask_app/
├── app.py                      # メインアプリケーション
├── models.py                   # データベースモデル
├── init_db.py                  # データベース初期化スクリプト
├── requirements.txt            # Python依存パッケージ
├── README.md                   # このファイル
├── instance/                   # データベースファイル（自動生成）
│   └── app.db
├── uploads/                    # アップロードファイル一時保存
├── templates/                  # HTMLテンプレート
│   ├── base.html              # ベーステンプレート
│   ├── index.html             # トップページ
│   ├── login.html             # ログインページ
│   ├── register.html          # 登録ページ
│   ├── request_login.html     # マジックリンクログイン
│   ├── dashboard.html         # ダッシュボード
│   ├── valuation.html         # 評価ツール（新版）
│   ├── history.html           # 評価履歴
│   ├── evaluate.html          # 評価ページ（旧版）
│   └── property_detail.html   # 物件詳細
└── static/                     # 静的ファイル（オプション）
    ├── css/
    ├── js/
    └── images/
```

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

### 2. 依存パッケージのインストール

```bash
cd flask_app
pip install -r requirements.txt
```

### 3. データベースの初期化

```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('データベースを初期化しました。')"
```

または:
```bash
python init_db.py
```

### 4. 環境変数の設定（オプション）

`.env`ファイルを作成して、シークレットキーを設定できます:
```bash
SECRET_KEY=your-secret-key-here
```

## 使用方法

### 開発サーバーの起動

```bash
python app.py
```

または

```bash
flask run
```

ブラウザで http://localhost:5000 にアクセスしてください。

### CLIコマンド

**データベースの初期化:**
```bash
flask init-db
```

**管理者ユーザーの作成:**
```bash
flask create-admin
```

## 主要な画面

### 1. トップページ (`/`)
- システムの概要と機能紹介
- ログイン/新規登録へのリンク

### 2. マジックリンクログイン (`/magic-login`)
- メールアドレスのみでログイン
- パスワード不要
- 15分間有効なログインリンクをメールで送信

### 3. ログイン (`/login`)
- 通常のログイン（メールアドレス + パスワード）
- マジックリンクログインへのリンク

### 4. ユーザー登録 (`/register`)
- 新規ユーザーアカウントの作成
- メールアドレスとパスワードで登録

### 5. ダッシュボード (`/dashboard`)
- 登録した物件の一覧表示
- 各物件の評価額サマリー
- 物件の削除

### 6. 評価ツール (`/valuation`)
- **ファイルアップロードタブ**: 画像をドラッグ&ドロップまたは選択
- **手動入力タブ**: フォームに直接入力
- リアルタイム評価額計算
- 結果の保存機能

### 7. 評価履歴 (`/history`)
- 過去の評価結果一覧（テーブル形式）
- ページネーション機能
- 統計情報の表示（総評価回数、平均評価額、最高評価額）

### 8. 物件詳細 (`/property/<id>`)
- 物件の詳細情報表示
- 土地・建物・合計の評価額表示

## API エンドポイント

### 認証
- `GET /login` - ログインページ
- `POST /login` - ログイン処理
- `GET /register` - 登録ページ
- `POST /register` - 登録処理
- `GET /magic-login` - マジックリンクログインページ
- `POST /magic-login` - マジックリンク送信
- `GET /callback?token=xxx` - マジックリンクコールバック
- `GET /logout` - ログアウト

### 評価機能
- `GET /valuation` - 評価ツールページ
- `POST /api/valuate` - 評価額計算API（JSON）
- `POST /valuation` - ファイルアップロード + OCR処理
- `POST /save_property` - 評価結果を保存

### 履歴
- `GET /history` - 評価履歴一覧
- `GET /history?page=2` - ページネーション

### その他
- `GET /` - トップページ
- `GET /dashboard` - ダッシュボード
- `GET /property/<id>` - 物件詳細
- `POST /property/<id>/delete` - 物件削除

## データベースモデル

### User（ユーザー）
- `id` - ユーザーID（主キー）
- `email` - メールアドレス（ユニーク）
- `password_hash` - パスワードハッシュ（マジックリンクの場合はNULL）
- `created_at` - 作成日時
- `updated_at` - 更新日時

### LoginToken（ログイントークン）
- `id` - トークンID（主キー）
- `user_email` - ユーザーメールアドレス
- `token` - トークン文字列（ユニーク）
- `expires_at` - 有効期限
- `used` - 使用済みフラグ
- `created_at` - 作成日時

### ValuationHistory（評価履歴）
- `id` - 履歴ID（主キー）
- `user_id` - ユーザーID（外部キー）
- `address` - 所在地
- `land_area` - 土地面積
- `total_floor_area` - 延床面積
- `building_structure` - 建物構造
- `build_year` - 建築年
- `land_valuation` - 土地評価額
- `building_valuation` - 建物評価額
- `total_valuation` - 合計評価額
- `road_price` - 路線価
- `created_at` - 作成日時

### Property（物件）
- `id` - 物件ID（主キー）
- `user_id` - ユーザーID（外部キー）
- `address` - 所在地
- `land_area` - 土地面積
- `building_structure` - 建物構造
- `total_floor_area` - 延床面積
- `build_year` - 建築年
- `land_valuation` - 土地評価額
- `building_valuation` - 建物評価額
- `total_valuation` - 合計評価額
- `created_at` - 作成日時
- `updated_at` - 更新日時

## セキュリティ

- **パスワードハッシュ化**: Werkzeug でハッシュ化して保存
- **セッション管理**: Flask-Loginによる安全なセッション管理
- **トークン生成**: secrets モジュールによるセキュアなトークン生成
- **CSRF対策**: Flask標準機能
- **SQLインジェクション対策**: SQLAlchemy ORM使用
- **ファイルアップロード制限**: 最大10MB、許可された拡張子のみ

## 本番環境へのデプロイ

### 環境変数の設定

```bash
export SECRET_KEY='ランダムな長い文字列'
export FLASK_ENV='production'
```

### WSGI サーバーの使用（Gunicorn推奨）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 開発コマンド

### データベースのリセット

```bash
rm instance/app.db
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 管理者ユーザーの作成

```bash
flask create-admin
```

## 注意事項

⚠️ **この評価額はあくまで推定値です。** 実際の固定資産税評価額は、地方自治体による評価に基づきます。

⚠️ **開発環境での使用**: 本番環境で使用する場合は、以下の設定を変更してください:
- `SECRET_KEY`を環境変数で設定（ランダムな長い文字列）
- `DEBUG=False`に設定
- PostgreSQLやMySQLなどの本番用データベースを使用
- **メール送信機能を実装**（現在はコンソールに出力）
  - SendGrid、Amazon SES、または SMTP サーバーを設定
  - マジックリンク機能を使用する場合は必須
- アップロードファイルのストレージを適切に設定（S3など）
- HTTPS を有効化
- セキュリティヘッダーを追加

## トラブルシューティング

### Tesseract が見つからない

```
pytesseract.pytesseract.TesseractNotFoundError
```

**解決方法**: Tesseract OCRをインストールしてください（上記のインストール手順を参照）

### データベースエラー

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table
```

**解決方法**: データベースを初期化してください
```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### ファイルアップロードエラー

**解決方法**: `uploads/` ディレクトリが存在し、書き込み権限があることを確認してください

## ライセンス

このプロジェクトは教育目的で作成されています。

## サポート

問題が発生した場合は、Issueを作成してください。
