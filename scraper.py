"""
国税庁ウェブサイトから路線価情報を取得するスクレイピング機能
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urljoin
import time


def get_rosenka_page_url(prefecture: str, city: str) -> Optional[str]:
    """
    国税庁のウェブサイトから指定された都道府県・市区町村の路線価図ページURLを取得

    Args:
        prefecture: 都道府県名（例: '東京都'）
        city: 市区町村名（例: '千代田区'）

    Returns:
        路線価図ページのURL、見つからない場合はNone
    """
    base_url = "https://www.rosenka.nta.go.jp/"

    try:
        # 1. トップページにアクセス
        print(f"トップページにアクセス中: {base_url}")
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2. 指定された都道府県のリンクを探す
        print(f"都道府県を検索中: {prefecture}")
        prefecture_link = None

        # 全てのリンクを探索
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if prefecture in link_text:
                prefecture_link = urljoin(base_url, link['href'])
                print(f"都道府県リンクを発見: {prefecture_link}")
                break

        if not prefecture_link:
            print(f"都道府県 '{prefecture}' のリンクが見つかりませんでした")
            return None

        # 少し待機（サーバーへの負荷軽減）
        time.sleep(1)

        # 3. 都道府県ページにアクセス
        print(f"都道府県ページにアクセス中: {prefecture_link}")
        response = requests.get(prefecture_link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 4. 路線価図のリンクを探す
        print("路線価図のリンクを検索中...")
        rosenka_link = None

        # 都道府県ページのベースURLを取得（相対パスの解決に使用）
        prefecture_base = '/'.join(prefecture_link.split('/')[:-1]) + '/'

        # 「路線価図」というテキストを持つリンクを探す（より厳密にマッチング）
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            href = link['href']
            # 「路線価図」と完全一致、かつ相対パス（prices/city_frm.htm等）を含むリンクを探す
            if link_text == '路線価図' and 'city_frm.htm' in href:
                rosenka_link = urljoin(prefecture_base, href)
                print(f"路線価図リンクを発見: {rosenka_link}")
                break

        if not rosenka_link:
            print("路線価図のリンクが見つかりませんでした")
            return None

        # 少し待機
        time.sleep(1)

        # 5. 路線価図ページにアクセス
        print(f"路線価図ページにアクセス中: {rosenka_link}")
        response = requests.get(rosenka_link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 6. 指定された市区町村のリンクを探す
        print(f"市区町村を検索中: {city}")
        city_link = None

        # 路線価図ページのベースURLを取得
        rosenka_base = '/'.join(rosenka_link.split('/')[:-1]) + '/'

        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if city in link_text:
                city_link = urljoin(rosenka_base, link['href'])
                print(f"市区町村リンクを発見: {city_link}")
                break

        if not city_link:
            print(f"市区町村 '{city}' のリンクが見つかりませんでした")
            return None

        return city_link

    except requests.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")
        return None
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return None


def test_scraper():
    """スクレイパーのテスト関数"""
    print("="*60)
    print("路線価スクレイパーのテスト")
    print("="*60)

    # テストケース
    test_cases = [
        ("東京都", "千代田区"),
        ("東京都", "渋谷区"),
    ]

    for prefecture, city in test_cases:
        print(f"\nテスト: {prefecture} {city}")
        print("-"*60)
        url = get_rosenka_page_url(prefecture, city)

        if url:
            print(f"✓ 成功: {url}")
        else:
            print(f"✗ 失敗: URLが取得できませんでした")

        print("-"*60)
        time.sleep(2)  # 次のテストまで待機


if __name__ == "__main__":
    test_scraper()
