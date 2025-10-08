"""
データベース初期化スクリプト
"""
import os
from app import app, db
from models import User, Property


def init_database():
    """データベースを初期化"""
    with app.app_context():
        # instanceディレクトリの作成（SQLiteの場合のみ）
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            instance_path = os.path.join(os.path.dirname(__file__), 'instance')
            os.makedirs(instance_path, exist_ok=True)

        # 既存のテーブルを削除して再作成
        print('データベーステーブルを作成中...')
        db.create_all()
        print('✓ データベーステーブルを作成しました。')

        # 初期データの投入（オプション）
        # 既にユーザーが存在する場合はスキップ
        if User.query.count() == 0:
            # 環境変数でテストユーザー作成を制御（本番環境では作成しない）
            create_test_user = os.environ.get('CREATE_TEST_USER', 'false').lower() == 'true'

            if create_test_user:
                from werkzeug.security import generate_password_hash

                test_user = User(
                    email='test@example.com',
                    password_hash=generate_password_hash('password123')
                )
                db.session.add(test_user)
                db.session.commit()

                print('✓ テストユーザーを作成しました。')
                print('  メールアドレス: test@example.com')
                print('  パスワード: password123')
            else:
                print('テストユーザーの作成をスキップしました。')
        else:
            print(f'\n既に {User.query.count()} 人のユーザーが登録されています。')

        print('\n初期化が完了しました！')


if __name__ == '__main__':
    init_database()
