"""
OCR機能の簡単なテスト
"""
from PIL import Image, ImageDraw, ImageFont
import os
from ocr_utils import extract_text_from_image, extract_text_with_confidence


def create_test_image():
    """テスト用の画像を作成"""
    # 白い背景の画像を作成
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)

    # テキストを描画
    test_text = """
物件情報

所在地: 東京都渋谷区渋谷1-1-1
土地面積: 150.5㎡
建物構造: 鉄筋コンクリート造
延床面積: 200.0㎡
建築年: 2015年
    """

    # デフォルトフォントを使用してテキストを描画
    y_position = 30
    for line in test_text.strip().split('\n'):
        draw.text((50, y_position), line, fill='black')
        y_position += 40

    # 画像を保存
    test_image_path = 'test_property_image.png'
    img.save(test_image_path)
    print(f"テスト画像を作成しました: {test_image_path}")

    return test_image_path


def test_ocr():
    """OCR機能をテスト"""
    print("="*60)
    print("OCR機能のテスト")
    print("="*60)

    # テスト画像を作成
    image_path = create_test_image()

    # OCR実行（基本）
    print("\n1. 基本的なテキスト抽出:")
    print("-"*60)
    text = extract_text_from_image(image_path)
    print(text)

    # OCR実行（詳細情報付き）
    print("\n2. 信頼度情報付きテキスト抽出:")
    print("-"*60)
    result = extract_text_with_confidence(image_path)
    print(f"抽出されたテキスト:\n{result['text']}")
    print(f"\n信頼度: {result['confidence']:.2f}%")
    print(f"単語数: {result.get('word_count', 0)}")

    # テスト画像を削除
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"\nテスト画像を削除しました: {image_path}")

    print("="*60)


if __name__ == "__main__":
    test_ocr()
