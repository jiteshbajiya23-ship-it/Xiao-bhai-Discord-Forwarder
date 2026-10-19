import requests, os, json, time

BOT = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
STATE = ".offset"

def get_offset():
    try:
        with open(STATE) as f:
            return int(f.read())
    except:
        return 0

def save_offset(o):
    with open(STATE, "w") as f:
        f.write(str(o))

def forward(post):
    if not post or "channel_post" not in post:
        return
    p = post["channel_post"]
    txt = (p.get("text") or p.get("caption") or "")[:1000]
    
    data = {"username": "Donghua Bot", "embeds": [{
        "title": "📰 New Update",
        "description": txt or "📢",
        "color": 0x1abc9c,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(p.get("date", time.time())))
    }]}
    
    if "photo" in p:
        fid = p["photo"][-1]["file_id"]
        fi = requests.get(f"https://api.telegram.org/bot{BOT}/getFile", params={"file_id": fid}).json()
        if fi.get("ok"):
            fp = fi["result"]["file_path"]
            data["embeds"][0]["image"] = {"url": f"https://api.telegram.org/file/bot{BOT}/{fp}"}
    
    if "video" in p:
        vid = p["video"]
        fid = vid.get("file_id")
        fi = requests.get(f"https://api.telegram.org/bot{BOT}/getFile", params={"file_id": fid}).json()
        if fi.get("ok"):
            fp = fi["result"]["file_path"]
            name = vid.get("file_name", "video")
            data["embeds"][0]["title"] = f"🎬 {name}"
            data["embeds"][0]["description"] = f"[Download](https://api.telegram.org/file/bot{BOT}/{fp})\n{txt}"
    
    requests.post(WEBHOOK, json=data)

def main():
    offset = get_offset()
    r = requests.get(f"https://api.telegram.org/bot{BOT}/getUpdates",
        params={"offset": offset+1, "limit": 10, "allowed_updates": ["channel_post"]})
    for u in r.json().get("result", []):
        forward(u)
        save_offset(u["update_id"])

if __name__ == "__main__":
    main()
