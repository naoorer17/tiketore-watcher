import requests
from bs4 import BeautifulSoup
import os
import json
import hashlib
import time
import datetime

url = 'https://tiketore.com/events/artist/52941'
webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

print("✅ チケトレ監視Bot 起動")
print(f"🔍 {url} を取得中...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# サイト取得 + リトライ最大3回
for i in range(3):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        break
    except Exception as e:
        print(f'❌ リトライ {i+1} 回目失敗: {e}')
        time.sleep(5)
else:
    print('❌ 全てのリトライに失敗しました')
    if webhook_url:
        requests.post(webhook_url, json={"content": f"❌ チケトレ取得失敗（3回リトライ失敗）: {url}"})
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')
ticket_cards = soup.select('.p-ticketItem')

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# チケット出品なしでも通知を送るよう変更
if not ticket_cards:
    print("🔍 チケット出品なし")
    if webhook_url:
        requests.post(webhook_url, json={"content": f"🔍 チケットはまだ出品されていません\n({now})"})
    exit(0)

# ハッシュ化して通知済みを管理
hash_path = 'notified_hashes.json'
if os.path.exists(hash_path):
    with open(hash_path, 'r') as f:
        notified_hashes = set(json.load(f))
else:
    notified_hashes = set()

new_hashes = set()
new_tickets = []

for card in ticket_cards:
    title = card.select_one('.p-ticketItem__title').get_text(strip=True)
    date = card.select_one('.p-ticketItem__date').get_text(strip=True)
    link = 'https://tiketore.com' + card.get('href')

    data = f"{title}-{date}-{link}"
    data_hash = hashlib.sha256(data.encode()).hexdigest()

    if data_hash not in notified_hashes:
        new_tickets.append(f"🎫 {title} | {date}\n🔗 {link}")
        new_hashes.add(data_hash)

if not new_tickets:
    print("🟡 新しいチケット出品なし")
    if webhook_url:
        requests.post(webhook_url, json={"content": f"🟡 新しいチケット出品はありませんでした\n({now})"})
    exit(0)

# Discord通知（新規出品あり）
message = "🎉 新しいチケット出品を検出！\n\n" + "\n\n".join(new_tickets)
res = requests.post(webhook_url, json={"content": message})

if res.status_code == 204:
    print("✅ Discordに通知送信成功")
else:
    print(f"❌ Discord通知失敗: {res.status_code} - {res.text}")

# 通知済みを保存
with open(hash_path, 'w') as f:
    json.dump(list(notified_hashes | new_hashes), f)