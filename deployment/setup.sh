#!/bin/bash
#
# Road Price Valuation System - 自動セットアップスクリプト
# Ubuntu/Debian系サーバー用
#
# 使用方法: sudo bash setup.sh
#

set -e  # エラーが発生したら中断

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Road Price Valuation System${NC}"
echo -e "${GREEN}自動セットアップスクリプト${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# root権限チェック
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}このスクリプトはroot権限で実行してください${NC}"
   echo "使用方法: sudo bash setup.sh"
   exit 1
fi

echo -e "${YELLOW}[1/9] システムパッケージを更新中...${NC}"
apt update
apt upgrade -y

echo -e "${YELLOW}[2/9] 必要なパッケージをインストール中...${NC}"
apt install -y python3 python3-pip python3-venv \
    nginx git tesseract-ocr tesseract-ocr-jpn \
    postgresql postgresql-contrib \
    ufw certbot python3-certbot-nginx

echo -e "${YELLOW}[3/9] PostgreSQLデータベースをセットアップ中...${NC}"
echo -n "データベースのパスワードを入力してください: "
read -s DB_PASSWORD
echo ""

sudo -u postgres psql -c "CREATE DATABASE road_price;" 2>/dev/null || echo "データベースは既に存在します"
sudo -u postgres psql -c "CREATE USER road_price_user WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "ユーザーは既に存在します"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE road_price TO road_price_user;"

echo -e "${YELLOW}[4/9] アプリケーション用ユーザーを作成中...${NC}"
useradd -m -s /bin/bash roadprice 2>/dev/null || echo "ユーザーは既に存在します"

echo -e "${YELLOW}[5/9] リポジトリをクローン中...${NC}"
if [ ! -d "/home/roadprice/road-price_v1" ]; then
    sudo -u roadprice git clone https://github.com/arkadia-japan/road-price_v1.git /home/roadprice/road-price_v1
else
    echo "リポジトリは既に存在します。スキップします。"
fi

echo -e "${YELLOW}[6/9] Python仮想環境をセットアップ中...${NC}"
cd /home/roadprice/road-price_v1
sudo -u roadprice python3 -m venv venv
sudo -u roadprice /home/roadprice/road-price_v1/venv/bin/pip install --upgrade pip
sudo -u roadprice /home/roadprice/road-price_v1/venv/bin/pip install -r requirements.txt

echo -e "${YELLOW}[7/9] 環境変数を設定中...${NC}"
SECRET_KEY=$(openssl rand -hex 32)
cat > /home/roadprice/road-price_v1/.env << EOF
SECRET_KEY=$SECRET_KEY
DATABASE_URL=postgresql://road_price_user:$DB_PASSWORD@localhost/road_price
FLASK_ENV=production
EOF
chown roadprice:roadprice /home/roadprice/road-price_v1/.env
chmod 600 /home/roadprice/road-price_v1/.env

echo -e "${YELLOW}[8/9] データベースを初期化中...${NC}"
cd /home/roadprice/road-price_v1
export $(cat .env | xargs)
sudo -u roadprice /home/roadprice/road-price_v1/venv/bin/python flask_app/init_db.py

echo -e "${YELLOW}[9/9] ログディレクトリを作成中...${NC}"
mkdir -p /var/log/road-price
chown roadprice:roadprice /var/log/road-price

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}セットアップ完了！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}次のステップ:${NC}"
echo ""
echo "1. systemdサービスを設定:"
echo "   sudo cp /home/roadprice/road-price_v1/deployment/road-price.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable road-price"
echo "   sudo systemctl start road-price"
echo ""
echo "2. Nginxを設定:"
echo "   sudo cp /home/roadprice/road-price_v1/deployment/nginx.conf /etc/nginx/sites-available/road-price"
echo "   sudo nano /etc/nginx/sites-available/road-price  # ドメイン名を編集"
echo "   sudo ln -s /etc/nginx/sites-available/road-price /etc/nginx/sites-enabled/"
echo "   sudo nginx -t"
echo "   sudo systemctl restart nginx"
echo ""
echo "3. ファイアウォールを設定:"
echo "   sudo ufw allow 'Nginx Full'"
echo "   sudo ufw allow OpenSSH"
echo "   sudo ufw enable"
echo ""
echo "4. SSL証明書を取得 (オプション):"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo -e "${GREEN}詳細は deployment/DEPLOYMENT.md を参照してください${NC}"
