"""
不動産評価額推定システム - Flaskアプリケーション
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Property, LoginToken, ValuationHistory

# プロジェクトルートディレクトリを取得
basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(basedir)

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 設定
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 最大10MB
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')

# アップロードフォルダの作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# データベースの初期化
db.init_app(app)

# Flask-Loginの初期化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'このページにアクセスするにはログインが必要です。'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """ユーザーローダー"""
    return User.query.get(int(user_id))


# ============================================================
# ルート定義
# ============================================================

@app.route('/')
def index():
    """トップページ"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # バリデーション
        if not email or not password:
            flash('メールアドレスとパスワードを入力してください。', 'error')
            return render_template('register.html')

        if password != password_confirm:
            flash('パスワードが一致しません。', 'error')
            return render_template('register.html')

        # ユーザーが既に存在するかチェック
        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは既に登録されています。', 'error')
            return render_template('register.html')

        # 新規ユーザーを作成
        user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        flash('アカウントが作成されました。ログインしてください。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash('ログインしました。', 'success')

            # next パラメータがあればそこにリダイレクト
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('メールアドレスまたはパスワードが正しくありません。', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """ログアウト"""
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('index'))


@app.route('/magic-login', methods=['GET', 'POST'])
def magic_login():
    """マジックリンクログイン（メールアドレス入力）"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')

        # バリデーション
        if not email:
            flash('メールアドレスを入力してください。', 'error')
            return render_template('request_login.html')

        # ユーザーが存在しない場合は新規作成
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                password_hash=None  # マジックリンクログインの場合はパスワード不要
            )
            db.session.add(user)
            db.session.commit()
            flash('新規アカウントを作成しました。', 'info')

        # ログイントークンを生成
        login_token = LoginToken.create_token(email, expiry_minutes=15)
        db.session.add(login_token)
        db.session.commit()

        # ログインURLを生成
        login_url = url_for('callback', token=login_token.token, _external=True)

        # メール送信（開発環境ではコンソールに出力）
        print("\n" + "=" * 70)
        print("マジックリンクログイン - メール送信")
        print("=" * 70)
        print(f"宛先: {email}")
        print(f"件名: ログインリンク - 不動産評価額推定システム")
        print("\n--- メール本文 ---")
        print(f"""
こんにちは、

不動産評価額推定システムへのログインリクエストを受け付けました。

以下のリンクをクリックしてログインしてください。
このリンクは15分間有効です。

{login_url}

このメールに心当たりがない場合は、無視してください。

---
不動産評価額推定システム
        """)
        print("=" * 70 + "\n")

        flash('ログイン用のリンクをメールで送信しました。メールを確認してください。', 'success')
        return render_template('request_login.html')

    return render_template('request_login.html')


@app.route('/callback')
def callback():
    """マジックリンクのコールバック処理"""
    token_string = request.args.get('token')

    if not token_string:
        flash('無効なリンクです。', 'error')
        return redirect(url_for('magic_login'))

    # トークンを検証
    login_token = LoginToken.query.filter_by(token=token_string).first()

    if not login_token:
        flash('無効なトークンです。', 'error')
        return redirect(url_for('magic_login'))

    if not login_token.is_valid():
        flash('トークンの有効期限が切れています。再度ログインをリクエストしてください。', 'error')
        return redirect(url_for('magic_login'))

    # トークンを使用済みにマーク
    login_token.mark_as_used()

    # ユーザーを取得してログイン
    user = User.query.filter_by(email=login_token.user_email).first()

    if not user:
        flash('ユーザーが見つかりません。', 'error')
        return redirect(url_for('magic_login'))

    # ログイン処理
    login_user(user, remember=True)
    db.session.commit()

    flash('ログインしました。', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    """ダッシュボード"""
    properties = current_user.properties.order_by(Property.created_at.desc()).all()
    return render_template('dashboard.html', properties=properties)


@app.route('/history')
@login_required
def history():
    """評価履歴一覧"""
    # ログイン中のユーザーの評価履歴を取得（新しい順）
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # ページネーション付きで取得
    pagination = current_user.valuation_history.order_by(
        ValuationHistory.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    histories = pagination.items

    return render_template('history.html',
                         histories=histories,
                         pagination=pagination)


@app.route('/valuation', methods=['GET', 'POST'])
@login_required
def valuation():
    """不動産評価ツール"""
    if request.method == 'POST':
        try:
            input_method = request.form.get('input_method')

            if input_method == 'file':
                # ファイルアップロード処理
                if 'file' not in request.files:
                    return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400

                file = request.files['file']
                if file.filename == '':
                    return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400

                # ファイルを一時保存
                import uuid
                from werkzeug.utils import secure_filename

                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)

                try:
                    # OCRでテキスト抽出
                    import sys
                    sys.path.insert(0, project_root)
                    from ocr_utils import extract_text_from_image
                    from text_parser import parse_property_info

                    extracted_text = extract_text_from_image(filepath)
                    property_info = parse_property_info(extracted_text)

                    # パース結果を確認
                    if not all([property_info.get('address'),
                               property_info.get('land_area'),
                               property_info.get('total_floor_area'),
                               property_info.get('building_structure'),
                               property_info.get('build_year')]):
                        return jsonify({
                            'success': False,
                            'error': '必要な情報を画像から抽出できませんでした。手動入力をお試しください。'
                        }), 400

                    address = property_info['address']
                    land_area = float(property_info['land_area'])
                    total_floor_area = float(property_info['total_floor_area'])
                    building_structure = property_info['building_structure']
                    build_year = int(property_info['build_year'])

                finally:
                    # 一時ファイルを削除
                    if os.path.exists(filepath):
                        os.remove(filepath)

            elif input_method == 'manual':
                # 手動入力処理
                address = request.form.get('address')
                land_area = float(request.form.get('land_area'))
                total_floor_area = float(request.form.get('total_floor_area'))
                building_structure = request.form.get('building_structure')
                build_year = int(request.form.get('build_year'))

            else:
                return jsonify({'success': False, 'error': '無効な入力方法です'}), 400

            # 評価額を計算
            import sys
            sys.path.insert(0, project_root)
            from property_data import PropertyData
            from valuation import calculate_building_valuation, calculate_land_valuation, get_rosenka_mock

            property_data = PropertyData(
                address=address,
                land_area=land_area,
                building_structure=building_structure,
                total_floor_area=total_floor_area,
                build_year=build_year
            )

            land_value = calculate_land_valuation(property_data)
            building_value = calculate_building_valuation(property_data)
            total_value = land_value + building_value
            road_price = get_rosenka_mock(address)

            # 結果を返す
            result = {
                'address': address,
                'land_area': land_area,
                'total_floor_area': total_floor_area,
                'building_structure': building_structure,
                'build_year': build_year,
                'land_valuation': int(land_value),
                'building_valuation': int(building_value),
                'total_valuation': int(total_value),
                'road_price': int(road_price)
            }

            return jsonify({'success': True, 'result': result})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500

    # GET リクエスト
    return render_template('valuation.html')


@app.route('/api/valuate', methods=['POST'])
@login_required
def api_valuate():
    """
    評価額計算API（JSON入出力）

    Request JSON:
    {
        "address": "所在地",
        "land_area": 土地面積（float）,
        "total_floor_area": 延床面積（float）,
        "building_structure": "建物構造",
        "build_year": 建築年（int）
    }

    Response JSON:
    {
        "success": true,
        "result": {
            "address": "所在地",
            "land_area": 土地面積,
            "total_floor_area": 延床面積,
            "building_structure": "建物構造",
            "build_year": 建築年,
            "land_valuation": 土地評価額,
            "building_valuation": 建物評価額,
            "total_valuation": 合計評価額,
            "road_price": 路線価
        }
    }
    """
    try:
        # JSONデータを取得
        data = request.get_json()

        # バリデーション
        required_fields = ['address', 'land_area', 'total_floor_area', 'building_structure', 'build_year']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'必須項目が不足しています: {", ".join(missing_fields)}'
            }), 400

        # データ型の変換とバリデーション
        try:
            address = str(data['address']).strip()
            land_area = float(data['land_area'])
            total_floor_area = float(data['total_floor_area'])
            building_structure = str(data['building_structure']).strip()
            build_year = int(data['build_year'])

            # 値の範囲チェック
            if land_area <= 0:
                return jsonify({'success': False, 'error': '土地面積は0より大きい値を入力してください'}), 400
            if total_floor_area <= 0:
                return jsonify({'success': False, 'error': '延床面積は0より大きい値を入力してください'}), 400
            if build_year < 1900 or build_year > 2025:
                return jsonify({'success': False, 'error': '建築年は1900年から2025年の範囲で入力してください'}), 400
            if building_structure not in ['木造', '鉄骨造', '鉄筋コンクリート造']:
                return jsonify({'success': False, 'error': '建物構造は「木造」「鉄骨造」「鉄筋コンクリート造」のいずれかを選択してください'}), 400

        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': f'データ形式が正しくありません: {str(e)}'}), 400

        # 評価額を計算
        import sys
        sys.path.insert(0, project_root)
        from property_data import PropertyData
        from valuation import calculate_building_valuation, calculate_land_valuation, get_rosenka_mock

        property_data = PropertyData(
            address=address,
            land_area=land_area,
            building_structure=building_structure,
            total_floor_area=total_floor_area,
            build_year=build_year
        )

        # 各評価額を計算
        land_value = calculate_land_valuation(property_data)
        building_value = calculate_building_valuation(property_data)
        total_value = land_value + building_value
        road_price = get_rosenka_mock(address)

        # 評価履歴をデータベースに保存
        history = ValuationHistory(
            user_id=current_user.id,
            address=address,
            land_area=land_area,
            total_floor_area=total_floor_area,
            building_structure=building_structure,
            build_year=build_year,
            land_valuation=land_value,
            building_valuation=building_value,
            total_valuation=total_value,
            road_price=road_price
        )
        db.session.add(history)
        db.session.commit()

        # 結果を返す
        result = {
            'id': history.id,
            'address': address,
            'land_area': land_area,
            'total_floor_area': total_floor_area,
            'building_structure': building_structure,
            'build_year': build_year,
            'land_valuation': int(land_value),
            'building_valuation': int(building_value),
            'total_valuation': int(total_value),
            'road_price': int(road_price),
            'created_at': history.created_at.isoformat()
        }

        return jsonify({'success': True, 'result': result}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'サーバーエラーが発生しました。しばらくしてから再度お試しください。'
        }), 500


@app.route('/save_property', methods=['POST'])
@login_required
def save_property():
    """評価結果を保存"""
    try:
        data = request.get_json()

        property_record = Property(
            user_id=current_user.id,
            address=data['address'],
            land_area=data['land_area'],
            building_structure=data['building_structure'],
            total_floor_area=data['total_floor_area'],
            build_year=data['build_year'],
            land_valuation=data['land_valuation'],
            building_valuation=data['building_valuation'],
            total_valuation=data['total_valuation']
        )

        db.session.add(property_record)
        db.session.commit()

        return jsonify({'success': True, 'property_id': property_record.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
    """評価額算出"""
    if request.method == 'POST':
        # フォームデータを取得
        address = request.form.get('address')
        land_area = float(request.form.get('land_area'))
        building_structure = request.form.get('building_structure')
        total_floor_area = float(request.form.get('total_floor_area'))
        build_year = int(request.form.get('build_year'))

        # 既存のモジュールをインポート
        import sys
        sys.path.insert(0, project_root)
        from property_data import PropertyData
        from valuation import calculate_building_valuation, calculate_land_valuation

        # 評価額を計算
        property_data = PropertyData(
            address=address,
            land_area=land_area,
            building_structure=building_structure,
            total_floor_area=total_floor_area,
            build_year=build_year
        )

        land_value = calculate_land_valuation(property_data)
        building_value = calculate_building_valuation(property_data)
        total_value = land_value + building_value

        # データベースに保存
        property_record = Property(
            user_id=current_user.id,
            address=address,
            land_area=land_area,
            building_structure=building_structure,
            total_floor_area=total_floor_area,
            build_year=build_year,
            land_valuation=land_value,
            building_valuation=building_value,
            total_valuation=total_value
        )
        db.session.add(property_record)
        db.session.commit()

        flash('評価額を計算しました。', 'success')
        return redirect(url_for('property_detail', property_id=property_record.id))

    return render_template('evaluate.html')


@app.route('/property/<int:property_id>')
@login_required
def property_detail(property_id):
    """物件詳細"""
    property_record = Property.query.get_or_404(property_id)

    # 自分の物件かチェック
    if property_record.user_id != current_user.id:
        flash('アクセス権限がありません。', 'error')
        return redirect(url_for('dashboard'))

    return render_template('property_detail.html', property=property_record)


@app.route('/property/<int:property_id>/delete', methods=['POST'])
@login_required
def property_delete(property_id):
    """物件削除"""
    property_record = Property.query.get_or_404(property_id)

    # 自分の物件かチェック
    if property_record.user_id != current_user.id:
        flash('アクセス権限がありません。', 'error')
        return redirect(url_for('dashboard'))

    db.session.delete(property_record)
    db.session.commit()

    flash('物件を削除しました。', 'success')
    return redirect(url_for('dashboard'))


# ============================================================
# エラーハンドラー
# ============================================================

@app.errorhandler(404)
def not_found_error(error):
    """404エラー"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラー"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ============================================================
# CLI コマンド
# ============================================================

@app.cli.command()
def init_db():
    """データベースの初期化"""
    db.create_all()
    print('データベースを初期化しました。')


@app.cli.command()
def create_admin():
    """管理者ユーザーの作成"""
    email = input('メールアドレス: ')
    password = input('パスワード: ')

    if User.query.filter_by(email=email).first():
        print('このメールアドレスは既に登録されています。')
        return

    user = User(
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    print(f'管理者ユーザー {email} を作成しました。')


if __name__ == '__main__':
    # instanceディレクトリの作成
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

    # 開発サーバーの起動
    app.run(debug=True, port=5000)
