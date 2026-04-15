import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import urllib.parse
from datetime import datetime

# UPDATED IDS AND NAMES
STATIONS = {
    "Batajnica": "16204", "Kamendin": "16203", "Zemun Polje": "16053", 
    "Altina": "16059", "Zemun": "16052", "Tosin Bunar": "16202", 
    "Novi Beograd": "16051", "Beograd Centar": "16050", 
    "Karadjordjev Park": "16208", "Vukov Spomenik": "16210", 
    "Pancevacki Most": "16013", "Krnjaca Most": "16214", 
    "Krnjaca": "16213", "Sebes": "16215", "Ovca": "16212",
    "Resnik": "16101", "Kijevo": "16207", "Knezevac": "16206", "Rakovica": "16001"
}

today = datetime.now().strftime("%d.%m.%Y")
master_trains = {}

def normalize_text(text):
    if not text: return ""
    text = text.replace('đ', 'dj').replace('Đ', 'Dj')
    return "".join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def scrape():
    # Use a session to persist cookies like a real browser
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'sr,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://w3.srbvoz.rs/redvoznje/',
        'Connection': 'keep-alive'
    })

    # Site-specific Cyrillic map for URLs
    cyr_names = {
        "Batajnica": "БАТАЈНИЦА", "Kamendin": "КАМЕНДИН", "Zemun Polje": "ЗЕМУН%20ПОЉЕ",
        "Altina": "АЛТИНА", "Zemun": "ЗЕМУН", "Tosin Bunar": "ТОШИН%20БУНАР",
        "Novi Beograd": "НОВИ%20БЕОГРАД", "Beograd Centar": "БЕОГРАД%20ЦЕНТАР",
        "Karadjordjev Park": "КАРАЂОРЂЕВ%20ПАРК", "Vukov Spomenik": "ВУКОВ%20СПОМЕНИК",
        "Pancevacki Most": "ПАНЧЕВАЧКИ%20МОСТ", "Krnjaca Most": "КРЊАЧА%20МОСТ",
        "Krnjaca": "КРЊАЧА", "Sebes": "СЕБЕШ", "Ovca": "ОВЧА",
        "Resnik": "РЕСНИК", "Kijevo": "КИЈЕВО", "Knezevac": "КНЕЖЕВАЦ", "Rakovica": "РАКОВИЦА"
    }

    for name, s_id in STATIONS.items():
        url_part = cyr_names.get(name)
        url = f"https://w3.srbvoz.rs/redvoznje//stanicni/{url_part}/{s_id}/{today}/0000/polazak/999/sr"
        
        try:
            print(f"Syncing {name}...")
            response = session.get(url, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # If site returns nothing, the rows will be empty
            rows = soup.find_all('tr')
            found_count = 0
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                
                # Check for train ID (usually 2nd column)
                raw_id = cols[1].get_text(strip=True)
                if not raw_id.isdigit(): continue
                
                # Filter for BG:Voz numbers (80xx, 81xx, or check first column text)
                raw_type = cols[0].get_text(strip=True).upper()
                if any(x in raw_type for x in ["BG", "БГ"]) or raw_id.startswith(('80', '81')):
                    dep_time = cols[2].get_text(strip=True)
                    direction = normalize_text(cols[3].get_text(strip=True).upper())
                    
                    line = "BG:voz 2" if any(k in direction for k in ["RESNIK", "MLADENOVAC", "LAZAREVAC", "REZNIK"]) else "BG:voz 1"

                    if raw_id not in master_trains:
                        master_trains[raw_id] = {
                            "train_id": raw_id,
                            "line": line,
                            "direction": direction,
                            "stops": []
                        }
                    
                    master_trains[raw_id]["stops"].append({"station": name, "departure": dep_time})
                    found_count += 1
            
            print(f"  -> Found {found_count} trains.")

        except Exception as e:
            print(f"  -> Error: {e}")

    output = list(master_trains.values())
    for train in output:
        train["stops"].sort(key=lambda x: x["departure"])

    with open('trains.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"\nCOMPLETED: {len(output)} trains found.")

if __name__ == "__main__":
    scrape()
