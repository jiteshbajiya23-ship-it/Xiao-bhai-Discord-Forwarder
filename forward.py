#!/usr/bin/env python3
"""
Telegram Channel -> Discord Forwarder (Simplified - no git push needed)
Forwards only posts from the last 5 minutes each run.
"""
import requests, os, time

BOT = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]

def forward_post(ps, txt):
    embeds = []
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ps.get("date", 0)))

    if "photo" in ps:
        fid = ps["photo"][-1]["file_id"]
        fi = requests.get(f"https://api.telegram.org/bot{BOT}/getFile", params={"file_id": fid}).json()
        if fi.get("ok"):
            fp = fi["result"]["file_path"]
            embeds.append({
                "title": "📸 New Photo",
                "description": txt[:200] or "📷",
                "image": {"url": f"https://api.telegram.org/file/bot{BOT}/{fp}"},
                "timestamp": ts
            })

    if "video" in ps:
        vid = ps["video"]
        fid = vid.get("file_id")
        fi = requests.get(f"https://api.telegram.org/bot{BOT}/getFile", params={"file_id": fid}).json()
        if fi.get("ok"):
            fp = fi["result"]["file_path"]
            name = vid.get("file_name", "video")
            embeds.append({
                "title": f"🎬 {name}",
                "description": f"[📥 Download](https://api.telegram.org/file/bot{BOT}/{fp})\n{txt[:400] or ''}",
                "timestamp": ts
            })

    if not embeds:
        embeds.append({
            "title": "📝 New Post",
            "description": txt or "📢",
            "timestamp": ts
        })

    requests.post(WEBHOOK, json={"username": "🎬 Donghua Updates", "embeds": embeds})
    return True

def main():
    # Get updates - most recent first, no offset needed
    r = requests.get(f"https://api.telegram.org/bot{BOT}/getUpdates",
        params={"limit": 50, "allowed_updates": ["channel_post"]})

    results = r.json().get("result", [])
    now = int(time.time())
    five_min_ago = now - 300  # 5 minutes ago
    forwarded = 0

    for u in results:
        ps = u.get("channel_post", {})
        post_time = ps.get("date", 0)

        # Only forward posts from last 5 minutes
        if post_time >= five_min_ago:
            txt = ps.get("text", "") or ps.get("caption", "")
            if forward_post(ps, txt):
                forwarded += 1

    print(f"Forwarded {forwarded} new posts" if forwarded else "No new posts in last 5 min")

if __name__ == "__main__":
    main()
