"""
不動産評価額算出プログラムのメインスクリプト
"""
from property_data import PropertyData
from valuation import calculate_building_valuation, calculate_land_valuation


def main() -> None:
    """メイン処理"""
    # サンプル物件データの作成
    sample_property = PropertyData(
        address="東京都渋谷区渋谷1-1-1",
        land_area=150.5,
        building_structure="鉄筋コンクリート造",
        total_floor_area=200.0,
        build_year=2015
    )

    # 物件情報の表示
    print(sample_property)

    # 評価額を計算
    land_value = calculate_land_valuation(sample_property)
    building_value = calculate_building_valuation(sample_property)
    total_value = land_value + building_value

    print("\n" + "="*50)
    print(f"土地の評価額: {land_value:,.0f}円")
    print(f"建物の評価額: {building_value:,.0f}円")
    print(f"合計評価額: {total_value:,.0f}円")
    print("="*50)


if __name__ == "__main__":
    main()
