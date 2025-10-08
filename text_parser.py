"""
OCR抽出テキストから不動産情報を解析するパーサー
"""
import re
from typing import Optional, Dict, Any


def parse_property_info(text: str) -> Dict[str, Any]:
    """
    OCRで抽出したテキストから不動産情報を解析

    Args:
        text: OCRで抽出したテキスト

    Returns:
        不動産情報の辞書 {
            'address': 所在地,
            'land_area': 土地面積,
            'total_floor_area': 延床面積,
            'building_structure': 建物構造,
            'build_year': 建築年
        }
    """
    result = {
        'address': None,
        'land_area': None,
        'total_floor_area': None,
        'building_structure': None,
        'build_year': None
    }

    # 1. 所在地の抽出
    result['address'] = extract_address(text)

    # 2. 土地面積の抽出
    result['land_area'] = extract_land_area(text)

    # 3. 延床面積の抽出
    result['total_floor_area'] = extract_floor_area(text)

    # 4. 建物構造の抽出
    result['building_structure'] = extract_structure(text)

    # 5. 建築年の抽出
    result['build_year'] = extract_build_year(text)

    return result


def extract_address(text: str) -> Optional[str]:
    """所在地を抽出"""
    # キーワードパターン
    keywords = ['所在地', 'Address', '住所', '物件所在地', '所在']

    for keyword in keywords:
        # キーワードの後の文字列を抽出（改行または次のキーワードまで）
        patterns = [
            rf'{keyword}[：:]\s*([^\n]+)',
            rf'{keyword}\s+([^\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                # 余分な記号や数字のみの文字列を除去
                address = re.sub(r'[・･]', '', address)
                # 都道府県名や区市町村が含まれているかチェック
                if any(pref in address for pref in ['都', '道', '府', '県', '区', '市', '町', '村', 'Tokyo', 'Osaka']):
                    if len(address) > 5:  # 最低限の長さチェック
                        return address

    return None


def extract_land_area(text: str) -> Optional[float]:
    """土地面積を抽出（㎡）"""
    keywords = ['土地面積', 'Land Area', '敷地面積', '土地', '敷地']

    for keyword in keywords:
        # パターン1: "土地面積：150.5㎡" や "Land Area: 180.5 square meters"
        patterns = [
            rf'{keyword}[：:\s]*([0-9]+\.?[0-9]*)\s*[㎡m²平方メートルsquare meters]',
            rf'{keyword}[：:\s]*([0-9]+\.?[0-9]*)\s*平方メートル',
            rf'{keyword}[：:\s]*([0-9]+\.?[0-9]*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # 妥当な範囲チェック（10-10000㎡）
                    if 10 <= value <= 10000:
                        return value
                except ValueError:
                    continue

    # パターン2: 数値のみで㎡が明記されている場合
    pattern = r'([0-9]+\.?[0-9]*)\s*[㎡平方メートル]'
    matches = re.findall(pattern, text)
    if matches:
        try:
            value = float(matches[0])
            if 10 <= value <= 10000:
                return value
        except ValueError:
            pass

    return None


def extract_floor_area(text: str) -> Optional[float]:
    """延床面積を抽出（㎡）"""
    keywords = ['延床面積', 'Total Floor Area', '延べ床面積', '建物面積', '床面積', '延床']

    for keyword in keywords:
        # 複数のパターンを試す
        patterns = [
            rf'{keyword}[：:\s]*([0-9]+\.?[0-9]*)\s*[㎡m²平方メートルsquare meters]',
            rf'{keyword}[：:\s]*([0-9]+\.?[0-9]*)\s*平方メートル',
            rf'{keyword}[：:\s]*([0-9]+\.?[0-9]*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # 妥当な範囲チェック（10-10000㎡）
                    if 10 <= value <= 10000:
                        return value
                except ValueError:
                    continue

    return None


def extract_structure(text: str) -> Optional[str]:
    """建物構造を抽出"""
    # 構造のパターンマッピング
    structure_patterns = {
        '木造': ['木造', 'W造', '木', 'Wood', 'Wooden'],
        '鉄骨造': ['鉄骨造', 'S造', '鉄骨', '軽量鉄骨', 'Steel'],
        '鉄筋コンクリート造': ['鉄筋コンクリート造', 'RC造', 'ＲＣ造', 'RC', '鉄筋コンクリート', 'SRC造', 'Reinforced Concrete']
    }

    # キーワード
    keywords = ['構造', 'Building Structure', '建物構造', 'Structure', '規模構造', '規模']

    # キーワード付近を探す
    for keyword in keywords:
        patterns_to_try = [
            rf'{keyword}[：:\s]*([^\n]+)',
            rf'{keyword}\s+([^\n]+)'
        ]

        for pattern in patterns_to_try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                structure_text = match.group(1).strip()
                # 構造パターンとマッチング
                for standard_name, patterns in structure_patterns.items():
                    for pat in patterns:
                        if pat.lower() in structure_text.lower():
                            return standard_name

    # キーワードなしでも構造を直接探す
    for standard_name, patterns in structure_patterns.items():
        for pattern in patterns:
            if pattern.lower() in text.lower():
                return standard_name

    return None


def extract_build_year(text: str) -> Optional[int]:
    """建築年を抽出（西暦）"""
    keywords = ['建築年', 'Construction Year', '築年月', '建築', '築', '竣工年', '竣工', 'Year']

    # 和暦変換テーブル（簡略版）
    era_conversion = {
        '令和': 2018,
        '平成': 1988,
        '昭和': 1925,
        '大正': 1911,
        '明治': 1867
    }

    for keyword in keywords:
        # 西暦パターン: "建築年：2015年" or "Construction Year: 2018"
        patterns = [
            rf'{keyword}[：:\s]*(19[0-9]{{2}}|20[0-9]{{2}})',
            rf'{keyword}\s+(19[0-9]{{2}}|20[0-9]{{2}})'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    year = int(match.group(1))
                    if 1950 <= year <= 2025:
                        return year
                except ValueError:
                    continue

        # 和暦パターン: "平成27年"
        for era, base_year in era_conversion.items():
            pattern = rf'{keyword}[：:\s]*{era}\s*([0-9]+)'
            match = re.search(pattern, text)
            if match:
                try:
                    era_year = int(match.group(1))
                    return base_year + era_year
                except ValueError:
                    continue

    # キーワードなしで西暦を探す
    pattern = r'(19[5-9][0-9]|20[0-2][0-9])\s*年'
    match = re.search(pattern, text)
    if match:
        try:
            year = int(match.group(1))
            # 妥当な年かチェック（1950-2025）
            if 1950 <= year <= 2025:
                return year
        except ValueError:
            pass

    return None


def test_parser():
    """パーサーのテスト"""
    test_text = """
    物件情報シート

    所在地：東京都渋谷区渋谷1-1-1
    土地面積：150.5㎡
    延床面積：200.0㎡
    建物構造：鉄筋コンクリート造
    建築年：2015年
    """

    print("="*60)
    print("テキストパーサーのテスト")
    print("="*60)
    print("\n入力テキスト:")
    print(test_text)
    print("\n抽出結果:")
    print("-"*60)

    result = parse_property_info(test_text)
    for key, value in result.items():
        print(f"{key}: {value}")

    print("="*60)


if __name__ == "__main__":
    test_parser()
