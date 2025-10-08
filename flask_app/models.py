"""
データベースモデル定義
"""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """ユーザーモデル"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=True)  # マジックリンクログインの場合はNULL可
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション（将来的に物件情報などを追加する場合）
    # properties = db.relationship('Property', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Property(db.Model):
    """物件情報モデル（将来的な拡張用）"""
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 物件情報
    address = db.Column(db.String(200), nullable=False)
    land_area = db.Column(db.Float, nullable=False)
    building_structure = db.Column(db.String(50), nullable=False)
    total_floor_area = db.Column(db.Float, nullable=False)
    build_year = db.Column(db.Integer, nullable=False)

    # 評価額
    land_valuation = db.Column(db.Float)
    building_valuation = db.Column(db.Float)
    total_valuation = db.Column(db.Float)

    # タイムスタンプ
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    user = db.relationship('User', backref=db.backref('properties', lazy='dynamic'))

    def __repr__(self):
        return f'<Property {self.address}>'

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address': self.address,
            'land_area': self.land_area,
            'building_structure': self.building_structure,
            'total_floor_area': self.total_floor_area,
            'build_year': self.build_year,
            'land_valuation': self.land_valuation,
            'building_valuation': self.building_valuation,
            'total_valuation': self.total_valuation,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class LoginToken(db.Model):
    """マジックリンク用ログイントークンモデル"""
    __tablename__ = 'login_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<LoginToken {self.user_email}>'

    @staticmethod
    def generate_token():
        """セキュアなトークンを生成"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_token(email, expiry_minutes=15):
        """新しいログイントークンを作成"""
        token = LoginToken(
            user_email=email,
            token=LoginToken.generate_token(),
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
        return token

    def is_valid(self):
        """トークンが有効かチェック"""
        return not self.used and datetime.utcnow() < self.expires_at

    def mark_as_used(self):
        """トークンを使用済みにマーク"""
        self.used = True


class ValuationHistory(db.Model):
    """評価履歴モデル"""
    __tablename__ = 'valuation_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # 物件情報
    address = db.Column(db.String(200), nullable=False)
    land_area = db.Column(db.Float, nullable=False)
    total_floor_area = db.Column(db.Float, nullable=False)
    building_structure = db.Column(db.String(50), nullable=False)
    build_year = db.Column(db.Integer, nullable=False)

    # 評価額
    land_valuation = db.Column(db.Float, nullable=False)
    building_valuation = db.Column(db.Float, nullable=False)
    total_valuation = db.Column(db.Float, nullable=False)
    road_price = db.Column(db.Float, nullable=False)

    # タイムスタンプ
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # リレーション
    user = db.relationship('User', backref=db.backref('valuation_history', lazy='dynamic'))

    def __repr__(self):
        return f'<ValuationHistory {self.address} - ¥{self.total_valuation:,.0f}>'

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address': self.address,
            'land_area': self.land_area,
            'total_floor_area': self.total_floor_area,
            'building_structure': self.building_structure,
            'build_year': self.build_year,
            'land_valuation': int(self.land_valuation),
            'building_valuation': int(self.building_valuation),
            'total_valuation': int(self.total_valuation),
            'road_price': int(self.road_price),
            'created_at': self.created_at.isoformat()
        }
