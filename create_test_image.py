"""
テスト用の物件情報画像を作成
"""
from PIL import Image, ImageDraw, ImageFont
import sys


def create_property_image(output_path: str = 'sample_property.png'):
    """物件情報を含むテスト画像を作成"""
    # 高解像度の白い背景の画像を作成
    width, height = 1200, 900
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # テキスト内容（シンプルな形式）
    title = "Property Information Sheet"
    property_info = [
        "",
        "Address: Tokyo-to Chiyoda-ku Marunouchi 1-1-1",
        "所在地: 東京都千代田区丸の内1-1-1",
        "",
        "Land Area: 180.5 square meters",
        "土地面積: 180.5平方メートル",
        "",
        "Total Floor Area: 250.0 square meters",
        "延床面積: 250.0平方メートル",
        "",
        "Building Structure: Reinforced Concrete",
        "建物構造: 鉄筋コンクリート造",
        "",
        "Construction Year: 2018",
        "建築年: 2018年",
        "",
    ]

    # タイトルを描画
    try:
        # システムフォントを試す（macOS）
        font_large = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 48)
        font_normal = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 32)
    except:
        # デフォルトフォント（文字化けする可能性あり）
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()

    # タイトルを中央に描画
    draw.text((width//2 - 120, 50), title, fill='black', font=font_large)

    # 区切り線
    draw.line([(50, 120), (width-50, 120)], fill='black', width=2)

    # 物件情報を描画
    y_position = 150
    for line in property_info:
        draw.text((80, y_position), line, fill='black', font=font_normal)
        y_position += 45

    # 画像を保存
    img.save(output_path)
    print(f"✓ テスト画像を作成しました: {output_path}")
    print(f"  サイズ: {width}x{height}px")
    print(f"  内容: 物件概要書（千代田区丸の内の物件）")

    return output_path


if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'sample_property.png'
    create_property_image(output_file)
