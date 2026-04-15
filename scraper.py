import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import urllib.parse
from datetime import datetime

# COMPLETELY VALIDATED STATION IDS FOR 'POLAZAK' ENDPOINT
STATIONS = {
    "Batajnica": "16204", 
    "Kamendin": "16203", 
    "Zemun Polje": "16053", 
    "Altina": "16059", 
    "Zemun": "16052", 
    "Tosin Bunar": "16202", 
    "Novi Beograd": "16051", 
    "Beograd Centar": "16050", 
    "Karadjordjev Park": "16208", 
    "Vukov Spomenik": "16210", 
    "Pancevacki Most": "16013", 
    "Krnjaca Most": "16214", 
    "Krnjaca": "16213", 
    "Sebes": "16215", 
    "Ovca": "16212",
    "Resnik": "16101", 
    "Kijevo": "16207", 
    "Knezevac": "16206", 
    "Rakovica": "16001"
}

today = datetime.now().strftime("%d.%m.%Y")
master_trains = {}

def normalize_text(text):
    if not text: return ""
    text = text.replace('đ', 'dj').replace('Đ', 'Dj')
    return "".join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def scrape():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Internal map to translate our clean keys to the website's expected URL format
    url_names = {
        "Tosin Bunar": "TOŠIN%20BUNAR",
        "Novi Beograd": "NOVI%20BEOGRAD",
        "Beograd Centar": "BEOGRAD%20CENTAR",
        "Karadjordjev Park": "KARAĐORĐEV%20PARK",
        "Vukov Spomenik": "VUKOV%20SPOMENIK",
        "Pancevacki Most": "PANČEVAČKI%20MOST",
        "Krnjaca Most": "KRNJAČA%20MOST",
        "Krnjaca": "KRNJAČA",
        "Sebes": "SEBEŠ",
        "Ovca": "OVČA",
        "Knezevac": "KNEŽEVAC",
        "Zemun Polje": "ZEMUN%20POLJE"
    }

    for name, s_id in STATIONS.items():
        # Get the URL name (encoded) or default to Uppercase name
        url_part = url_names.get(name, name.upper())
        url = f"https://w3.srbvoz.rs/redvoznje//stanicni/{url_part}/{s_id}/{today}/0000/polazak/999/sr"
        
        try:
            print(f"Syncing {name}...")
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            found_count = 0
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                
                raw_type = cols[0].get_text(strip=True).upper()
                raw_id = cols[1].get_text(strip=True)
                
                # Check for BG:VOZ marker OR 80xx/81xx train numbers
                if any(x in raw_type for x in ["BG", "БГ"]) or raw_id.startswith('80') or raw_id.startswith('81'):
                    dep_time = cols[2].get_text(strip=True)
                    direction = normalize_text(cols[3].get_text(strip=True).upper())
                    note = cols[4].get_text(strip=True) if len(cols) > 4 else ""

                    # Automatic Line Detection
                    if any(k in direction for k in ["RESNIK", "MLADENOVAC", "LAZAREVAC", "SOPOт"]):
                        line = "BG:voz 2"
                    else:
                        line = "BG:voz 1"

                    if raw_id not in master_trains:
                        master_trains[raw_id] = {
                            "train_id": raw_id,
                            "line": line,
                            "direction": direction,
                            "note": note,
                            "stops": []
                        }
                    
                    # Prevent duplicate data if station is hit twice
                    if not any(s['station'] == name for s in master_trains[raw_id]["stops"]):
                        master_trains[raw_id]["stops"].append({"station": name, "departure": dep_time})
                        found_count += 1
            
            if found_count > 0:
                print(f"  -> Found {found_count} trains.")
            else:
                print(f"  -> No BG:VOZ found at this moment.")

        except Exception as e:
            print(f"  -> Error: {e}")

    # Sort and save
    output = list(master_trains.values())
    for train in output:
        train["stops"].sort(key=lambda x: x["departure"])

    with open('trains.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"\nSUCCESS: {len(output)} total trains compiled.")

if __name__ == "__main__":
    scrape()
