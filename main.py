# Python 3.10+, GitHub Actions — rscripts.net → Discord
import os
import time
import requests

# --- YOUR WEBHOOK ---
RSCRIPTS_WEBHOOK = "https://discord.com/api/webhooks/1563122870329024535/v7NZq-eiGFhcvBiyMTgIPliLG3ftJO8JgmeVf44AiJ1FJ1Es21buBb7Xpcl01TXDzpdx"

# --- YOUR API KEY ---
RSCRIPTS_API_KEY = "rsc_live_ay0UkSSpt3K5pyA_uboZoHyMgZ017O2e"
RSCRIPTS_API = "https://api.rscripts.net/v1/scripts"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Authorization": f"Bearer {RSCRIPTS_API_KEY}"
}

SEEN_FILE = "rscripts_seen.txt"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(seen))

def send_discord(title, description, url):
    payload = {
        "embeds": [{
            "title": title[:256],
            "url": url,
            "description": description[:2048],
            "color": 0xE74C3C,
            "footer": {"text": "rscripts.net"}
        }]
    }
    try:
        r = requests.post(RSCRIPTS_WEBHOOK, json=payload, headers=HEADERS, timeout=15)
        print(f"[hook] {r.status_code} :: {title[:60]}")
        time.sleep(1)
    except Exception as e:
        print(f"[hook] error: {e}")

def check_rscripts():
    print("[rscripts] checking...")
    seen = load_seen()
    baseline = not seen 

    try:
        # Fetch the newest scripts
        url = f"{RSCRIPTS_API}?sort=newest&limit=48&page=1"
        r = requests.get(url, headers=HEADERS, timeout=20)
        
        if r.status_code != 200:
            print(f"[rscripts] error: status {r.status_code} - {r.text[:100]}")
            return

        data = r.json()
        scripts = data.get("data", [])
        
        for s in scripts:
            sid = str(s.get("id"))
            if not sid or sid in seen:
                continue
            
            if baseline:
                seen.add(sid)
                continue
            
            title = s.get("title", "Unknown Script")
            slug = s.get("slug", "")
            link = f"https://rscripts.net/script/{slug}" if slug else f"https://rscripts.net/script/{sid}"
            
            game = s.get("game", {}).get("title", "Unknown Game")
            risk = s.get("risk", {})
            risk_level = risk.get("level", "Unknown")
            is_obfuscated = risk.get("isObfuscated", False)
            
            desc = f"**Game:** {game}\n**Risk:** {risk_level}\n**Obfuscated:** {is_obfuscated}"
            
            send_discord(title, desc, link)
            seen.add(sid)
            
    except Exception as e:
        print(f"[rscripts] error: {e}")

    if baseline:
        print(f"[rscripts] baseline: {len(seen)} cached, no pings")
    
    save_seen(seen)

if __name__ == "__main__":
    print("Starting rscripts bot...")
    start_time = time.time()
    
    # Runs for ~5 hours 50 minutes
    while time.time() - start_time < 21000:
        check_rscripts()
        print("Sleeping for 60 seconds...")
        time.sleep(60) # Changed to 60 seconds
