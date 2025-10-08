"""
OCR→パーサーの完全なパイプラインをテスト
"""
from ocr_utils import extract_text_with_confidence
from text_parser import parse_property_info


def test_pipeline(image_path: str = 'sample_property.png'):
    """完全なパイプラインをテスト"""
    print("="*60)
    print("OCR→パーサー パイプラインのテスト")
    print("="*60)

    # 1. OCRでテキスト抽出
    print(f"\n1. 画像からテキストを抽出: {image_path}")
    print("-"*60)
    result = extract_text_with_confidence(image_path)

    if 'error' in result:
        print(f"エラー: {result['error']}")
        return

    print(f"抽出されたテキスト:\n{result['text']}")
    print(f"\n信頼度: {result['confidence']:.1f}%")

    # 2. テキストをパース
    print("\n2. テキストから物件情報を解析")
    print("-"*60)
    parsed_info = parse_property_info(result['text'])

    print("解析結果:")
    for key, value in parsed_info.items():
        status = "✓" if value is not None else "✗"
        label = {
            'address': '所在地',
            'land_area': '土地面積',
            'total_floor_area': '延床面積',
            'building_structure': '建物構造',
            'build_year': '建築年'
        }.get(key, key)
        print(f"  {status} {label}: {value}")

    print("="*60)


if __name__ == "__main__":
    import sys
    image_path = sys.argv[1] if len(sys.argv) > 1 else 'sample_property.png'
    test_pipeline(image_path)
