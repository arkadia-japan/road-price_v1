#!/usr/bin/env bash
# exit on error
set -o errexit

# Tesseract OCRのインストール
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-jpn

# Pythonパッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt

# データベースのマイグレーション（初期化）
python flask_app/init_db.py
