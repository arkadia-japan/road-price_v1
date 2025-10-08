"""
不動産評価額算出アプリ（Streamlit UI）
"""
import streamlit as st
from PIL import Image
from property_data import PropertyData
from valuation import calculate_building_valuation, calculate_land_valuation
from ocr_utils import extract_text_from_image, extract_text_with_confidence
from text_parser import parse_property_info


def main() -> None:
    """メイン処理"""
    st.title("🏠 不動産評価額推定システム")
    st.write("物件情報を入力して、評価額を推定します。")

    # セッションステートの初期化
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = {
            'address': '東京都渋谷区渋谷1-1-1',
            'land_area': 150.5,
            'total_floor_area': 200.0,
            'building_structure': '鉄筋コンクリート造',
            'build_year': 2015
        }

    # 画像アップロード機能
    st.header("📷 物件資料の読み込み（オプション）")
    st.write("物件資料の画像ファイルをアップロードすると、テキストを自動抽出します。")

    uploaded_file = st.file_uploader(
        "画像ファイルを選択してください",
        type=['jpg', 'jpeg', 'png'],
        help="JPEG、PNG形式の画像ファイルに対応しています"
    )

    if uploaded_file is not None:
        # 画像を表示
        image = Image.open(uploaded_file)
        st.image(image, caption='アップロードされた画像', use_container_width=True)

        # OCR処理
        with st.spinner('画像からテキストを抽出中...'):
            # ファイルポインタを先頭に戻す
            uploaded_file.seek(0)
            result = extract_text_with_confidence(uploaded_file)

        if 'error' in result:
            st.error(f"エラー: {result['error']}")
        else:
            st.success(f"✓ テキスト抽出完了（信頼度: {result['confidence']:.1f}%）")

            # 抽出されたテキストを表示
            st.subheader("抽出されたテキスト")
            if result['text']:
                st.text_area(
                    "OCR結果",
                    value=result['text'],
                    height=200,
                    help="画像から抽出されたテキストです。必要に応じて下のフォームに手動で入力してください。"
                )

                # テキストから物件情報を解析
                st.subheader("🔍 情報の自動抽出")
                with st.spinner('物件情報を解析中...'):
                    parsed_info = parse_property_info(result['text'])

                # 抽出された情報を表示
                extracted_count = sum(1 for v in parsed_info.values() if v is not None)
                if extracted_count > 0:
                    st.success(f"✓ {extracted_count}件の情報を自動抽出しました")

                    # セッションステートを更新（Noneでない値のみ）
                    for key, value in parsed_info.items():
                        if value is not None:
                            st.session_state.parsed_data[key] = value

                    # 抽出された情報を表示
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("**抽出された情報:**")
                        for key, value in parsed_info.items():
                            if value is not None:
                                label = {
                                    'address': '所在地',
                                    'land_area': '土地面積',
                                    'total_floor_area': '延床面積',
                                    'building_structure': '建物構造',
                                    'build_year': '建築年'
                                }.get(key, key)
                                st.write(f"- {label}: {value}")

                    with cols[1]:
                        st.info("📝 下のフォームに自動入力されました。\n必要に応じて修正してください。")
                else:
                    st.warning("物件情報を自動抽出できませんでした。手動で入力してください。")
            else:
                st.warning("テキストが検出されませんでした。画像の品質を確認してください。")

    st.divider()

    # 入力フォーム
    st.header("物件情報の入力")

    # セッションステートから値を取得
    parsed_data = st.session_state.parsed_data

    with st.form("property_form"):
        # 所在地
        address = st.text_input(
            "所在地",
            value=parsed_data.get('address', '東京都渋谷区渋谷1-1-1'),
            placeholder="例: 東京都渋谷区渋谷1-1-1"
        )

        # 土地面積
        land_area = st.number_input(
            "土地面積（㎡）",
            min_value=0.0,
            value=float(parsed_data.get('land_area', 150.5)),
            step=0.1,
            format="%.1f"
        )

        # 建物の構造
        structure_options = ["木造", "鉄骨造", "鉄筋コンクリート造"]
        default_structure = parsed_data.get('building_structure', '鉄筋コンクリート造')
        structure_index = structure_options.index(default_structure) if default_structure in structure_options else 2

        building_structure = st.selectbox(
            "建物の構造",
            options=structure_options,
            index=structure_index
        )

        # 延床面積
        total_floor_area = st.number_input(
            "延床面積（㎡）",
            min_value=0.0,
            value=float(parsed_data.get('total_floor_area', 200.0)),
            step=0.1,
            format="%.1f"
        )

        # 建築年
        build_year = st.number_input(
            "建築年",
            min_value=1900,
            max_value=2025,
            value=int(parsed_data.get('build_year', 2015)),
            step=1
        )

        # 送信ボタン
        submitted = st.form_submit_button("評価額を計算")

    # 計算実行
    if submitted:
        # PropertyDataオブジェクトを作成
        property_data = PropertyData(
            address=address,
            land_area=land_area,
            building_structure=building_structure,
            total_floor_area=total_floor_area,
            build_year=build_year
        )

        # 評価額を計算
        land_value = calculate_land_valuation(property_data)
        building_value = calculate_building_valuation(property_data)
        total_value = land_value + building_value

        # 結果表示
        st.header("評価額の推定結果")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="土地の評価額",
                value=f"{land_value:,.0f}円"
            )

        with col2:
            st.metric(
                label="建物の評価額",
                value=f"{building_value:,.0f}円"
            )

        with col3:
            st.metric(
                label="合計評価額",
                value=f"{total_value:,.0f}円"
            )

        # 入力内容の確認
        st.subheader("入力内容の確認")
        st.write(property_data)

        # 免責事項
        st.warning("⚠️ この評価額はあくまで推定値です")
        st.info(
            "実際の固定資産税評価額は、地方自治体による評価に基づきます。"
            "本システムの推定値は参考値としてご利用ください。"
        )


if __name__ == "__main__":
    main()
