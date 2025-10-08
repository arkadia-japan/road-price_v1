"""
画像からテキストを抽出するOCRユーティリティ
"""
from PIL import Image
import pytesseract
from typing import Optional
import io


def extract_text_from_image(image_file, lang: str = 'jpn+eng') -> str:
    """
    画像からテキストを抽出する

    Args:
        image_file: 画像ファイル（BytesIOオブジェクトまたはファイルパス）
        lang: Tesseractで使用する言語（デフォルト: 'jpn+eng'で日本語と英語）

    Returns:
        抽出されたテキスト
    """
    try:
        # 画像を開く
        if isinstance(image_file, (str, bytes)):
            image = Image.open(image_file)
        else:
            # BytesIOまたはUploadedFileオブジェクトの場合
            image = Image.open(image_file)

        # RGBモードに変換（必要に応じて）
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # OCR実行
        text = pytesseract.image_to_string(image, lang=lang)

        return text.strip()

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


def extract_text_with_confidence(image_file, lang: str = 'jpn+eng') -> dict:
    """
    画像からテキストを抽出し、信頼度情報も取得する

    Args:
        image_file: 画像ファイル（BytesIOオブジェクトまたはファイルパス）
        lang: Tesseractで使用する言語

    Returns:
        テキストと信頼度情報を含む辞書
    """
    try:
        # 画像を開く
        if isinstance(image_file, (str, bytes)):
            image = Image.open(image_file)
        else:
            image = Image.open(image_file)

        # RGBモードに変換
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # OCR実行（詳細データを取得）
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)

        # テキストを結合
        text = pytesseract.image_to_string(image, lang=lang)

        # 信頼度の平均を計算（-1以外の値のみ）
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            'text': text.strip(),
            'confidence': avg_confidence,
            'word_count': len([w for w in data['text'] if w.strip()])
        }

    except Exception as e:
        return {
            'text': '',
            'confidence': 0,
            'error': str(e)
        }


if __name__ == "__main__":
    print("OCRユーティリティモジュール")
    print("使用可能な関数:")
    print("- extract_text_from_image(image_file, lang='jpn+eng')")
    print("- extract_text_with_confidence(image_file, lang='jpn+eng')")
