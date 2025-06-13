import requests
from bs4 import BeautifulSoup
import os

URL = "https://tiketore.com/events/artist/52941"
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]

def send_discord_alert(message):
    payload = {"content": message}
    requests.post(WEBHOOK, json=payload)

def get_items():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")
    return [li.get_text(strip=True) for li in soup.select("ul.ticket-list li")]

try:
    old_items = set(open("latest.txt").read().splitlines())
except:
    old_items = set()

new_items = set(get_items())
diff = new_items - old_items

for item in diff:
    send_discord_alert(f"🎫 新しいチケット出品：\n{item}\n{URL}")

with open("latest.txt", "w") as f:
    f.write("\n".join(new_items))