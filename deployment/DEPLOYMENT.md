# 自前サーバーへのデプロイ手順

Ubuntu/Debian系サーバーへのFlask Webアプリケーションのデプロイ手順です。

## 前提条件

- Ubuntu 20.04 / 22.04 または Debian 11/12
- sudoアクセス権限
- ドメイン名（オプション、SSL証明書用）

## 1. サーバーの準備

### システムパッケージの更新

```bash
sudo apt update
sudo apt upgrade -y
```

### 必要なパッケージのインストール

```bash
sudo apt install -y python3 python3-pip python3-venv \
    nginx git tesseract-ocr tesseract-ocr-jpn \
    postgresql postgresql-contrib
```

## 2. PostgreSQLデータベースのセットアップ

### データベースとユーザーの作成

```bash
sudo -u postgres psql
```

PostgreSQLプロンプトで以下を実行：

```sql
CREATE DATABASE road_price;
CREATE USER road_price_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE road_price TO road_price_user;
\q
```

## 3. アプリケーションのデプロイ

### アプリケーション用ユーザーの作成

```bash
sudo useradd -m -s /bin/bash roadprice
sudo su - roadprice
```

### リポジトリのクローン

```bash
cd /home/roadprice
git clone https://github.com/arkadia-japan/road-price_v1.git
cd road-price_v1
```

### 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate
```

### 依存パッケージのインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 環境変数の設定

```bash
cat > .env << 'EOF'
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://road_price_user:your-secure-password@localhost/road_price
FLASK_ENV=production
EOF
```

**.envファイルを編集**して、`your-secure-password`を実際のパスワードに置き換えてください。

```bash
nano .env
```

### データベースの初期化

```bash
export $(cat .env | xargs)
python flask_app/init_db.py
```

### アプリケーションのテスト

```bash
gunicorn --chdir flask_app --bind 0.0.0.0:8000 app:app
```

ブラウザで `http://サーバーIP:8000` にアクセスして動作確認。
確認後、Ctrl+Cで停止。

ユーザーを元に戻す：
```bash
exit  # roadpriceユーザーから抜ける
```

## 4. systemdサービスの設定

### サービスファイルの配置

```bash
sudo cp /home/roadprice/road-price_v1/deployment/road-price.service /etc/systemd/system/
```

### サービスの有効化と起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable road-price
sudo systemctl start road-price
sudo systemctl status road-price
```

## 5. Nginxの設定

### Nginx設定ファイルの配置

```bash
sudo cp /home/roadprice/road-price_v1/deployment/nginx.conf /etc/nginx/sites-available/road-price
```

### 設定ファイルの編集（ドメイン名を変更）

```bash
sudo nano /etc/nginx/sites-available/road-price
```

`server_name`の箇所を実際のドメイン名またはIPアドレスに変更：

```nginx
server_name your-domain.com;  # または IPアドレス
```

### サイトの有効化

```bash
sudo ln -s /etc/nginx/sites-available/road-price /etc/nginx/sites-enabled/
sudo nginx -t  # 設定ファイルの文法チェック
sudo systemctl restart nginx
```

### ファイアウォールの設定（UFW使用の場合）

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## 6. SSL証明書の設定（Let's Encrypt）

### Certbotのインストール

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### SSL証明書の取得

```bash
sudo certbot --nginx -d your-domain.com
```

メールアドレスを入力し、利用規約に同意します。

### 自動更新の確認

```bash
sudo certbot renew --dry-run
```

## 7. デプロイ完了

ブラウザで以下にアクセス：
- HTTP: `http://your-domain.com`
- HTTPS: `https://your-domain.com`

## 運用コマンド

### アプリケーションの再起動

```bash
sudo systemctl restart road-price
```

### ログの確認

```bash
# アプリケーションログ
sudo journalctl -u road-price -f

# Nginxアクセスログ
sudo tail -f /var/log/nginx/access.log

# Nginxエラーログ
sudo tail -f /var/log/nginx/error.log
```

### アプリケーションの更新

```bash
sudo su - roadprice
cd /home/roadprice/road-price_v1
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
exit

sudo systemctl restart road-price
```

### データベースのバックアップ

```bash
sudo -u postgres pg_dump road_price > backup_$(date +%Y%m%d_%H%M%S).sql
```

### データベースのリストア

```bash
sudo -u postgres psql road_price < backup_YYYYMMDD_HHMMSS.sql
```

## トラブルシューティング

### サービスが起動しない

```bash
sudo systemctl status road-price
sudo journalctl -u road-price -n 50
```

### データベース接続エラー

```bash
# PostgreSQLの状態確認
sudo systemctl status postgresql

# データベース接続テスト
sudo -u postgres psql -d road_price -c "SELECT version();"
```

### Nginxエラー

```bash
# Nginx設定テスト
sudo nginx -t

# エラーログ確認
sudo tail -f /var/log/nginx/error.log
```

## セキュリティ推奨事項

1. **ファイアウォール設定**: 必要なポートのみ開放
2. **SSH鍵認証**: パスワード認証を無効化
3. **定期的な更新**: システムパッケージとアプリケーションの更新
4. **バックアップ**: データベースの定期的なバックアップ
5. **ログ監視**: アプリケーションとサーバーのログを定期的に確認
6. **強力なパスワード**: データベースとSECRET_KEYに強力な値を使用

## パフォーマンス最適化

### Gunicornワーカー数の調整

`/etc/systemd/system/road-price.service`を編集：

```ini
# ワーカー数 = (2 × CPUコア数) + 1
ExecStart=/home/roadprice/road-price_v1/venv/bin/gunicorn --workers 5 --chdir /home/roadprice/road-price_v1/flask_app --bind unix:/home/roadprice/road-price_v1/road-price.sock app:app
```

### PostgreSQLのチューニング

```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

メモリに応じて調整：
```
shared_buffers = 256MB
effective_cache_size = 1GB
```

```bash
sudo systemctl restart postgresql
```
