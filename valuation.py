"""
不動産評価額算出ロジック
"""
from datetime import datetime
from property_data import PropertyData


def calculate_building_valuation(property_data: PropertyData) -> float:
    """
    建物の固定資産税評価額を推定する

    Args:
        property_data: 物件情報

    Returns:
        建物の評価額（円）
    """
    # 1. 再建築費の単価を決定
    unit_costs = {
        '木造': 150000,
        '鉄骨造': 180000,
        '鉄筋コンクリート造': 200000
    }
    unit_cost = unit_costs.get(property_data.building_structure, 150000)

    # 2. 経年減点補正率を決定
    current_year = datetime.now().year
    age = current_year - property_data.build_year

    # 構造別の耐用年数と最低補正率
    depreciation_params = {
        '木造': {'max_years': 22, 'min_rate': 0.2},
        '鉄骨造': {'max_years': 34, 'min_rate': 0.2},
        '鉄筋コンクリート造': {'max_years': 47, 'min_rate': 0.2}
    }

    # デフォルトは木造
    params = depreciation_params.get(
        property_data.building_structure,
        depreciation_params['木造']
    )

    max_years = params['max_years']
    min_rate = params['min_rate']

    if age <= 0:
        depreciation_rate = 1.0
    elif age >= max_years:
        depreciation_rate = min_rate
    else:
        # 直線的に減少: 1.0 → min_rate
        annual_decrease = (1.0 - min_rate) / max_years
        depreciation_rate = 1.0 - (age * annual_decrease)

    # 3. 評価額を計算
    valuation = unit_cost * property_data.total_floor_area * depreciation_rate

    return valuation


def get_rosenka_mock(address: str) -> float:
    """
    路線価を取得する（モック関数）

    Args:
        address: 物件の所在地

    Returns:
        路線価（円/㎡）
    """
    # 現時点では固定値を返す
    return 300000


def calculate_land_valuation(property_data: PropertyData) -> float:
    """
    土地の固定資産税評価額を推定する

    Args:
        property_data: 物件情報

    Returns:
        土地の評価額（円）
    """
    # 1. 路線価を取得（モック）
    rosenka = get_rosenka_mock(property_data.address)

    # 2. 固定資産税路線価を推定（相続税路線価の70%）
    fixed_asset_rosenka = rosenka * 0.7

    # 3. 補正率（現時点では1.0固定）
    correction_rate = 1.0

    # 4. 評価額を計算
    valuation = fixed_asset_rosenka * property_data.land_area * correction_rate

    return valuation
