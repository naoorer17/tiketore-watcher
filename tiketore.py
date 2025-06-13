import os
import requests
from bs4 import BeautifulSoup

def main():
    print("✅ チケトレ監視Bot 起動")

    url = "https://tiketore.com/events/artist/52941"
    print(f"🔍 {url} を取得中...")
    try:
        res = requests.get(url)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ サイト取得失敗: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")

    # 出品があるかどうか判定（適宜、サイト構造に合わせて調整してください）
    tickets = soup.select(".event-list__item")  # 例: チケットのリスト
    if tickets:
        print(f"🎉 {len(tickets)} 件のチケット出品を検出")

        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            print("❌ DISCORD_WEBHOOK_URL が設定されていません")
            return

        content = f"🎫 チケットが出品されました！\n{url}"
        try:
            response = requests.post(webhook_url, json={"content": content})
            response.raise_for_status()
            print("✅ Discordに通知送信成功")
        except Exception as e:
            print(f"❌ Discord通知失敗: {e}")
    else:
        print("ℹ️ チケット出品はありませんでした")

if __name__ == "__main__":
    main()