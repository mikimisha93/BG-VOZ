import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import urllib.parse  # Added for proper URL encoding
from datetime import datetime

# Updated with the specific IDs from your links
STATIONS = {
    "Batajnica": "16204", "Kamendin": "16203", "Zemun Polje": "16053", 
    "Altina": "16059", "Zemun": "16052", "Tosin Bunar": "16202", 
    "Novi Beograd": "16051", "Beograd Centar": "16050", 
    "Karadjordjev Park": "16208", "Vukov Spomenik": "16210", 
    "Pancevacki Most": "16013",  # Updated to match your link
    "Krnjaca Most": "16214", "Krnjaca": "16213", 
    "Sebes": "16215", "Ovca": "16212",
    "Resnik": "16101", "Kijevo": "16207", "Kneževac": "16206", "Rakovica": "16001"
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

    for name, s_id in STATIONS.items():
        # Map the Latin names back to the required Cyrillic/Accented names for the URL
        url_name_map = {
            "Tosin Bunar": "TOŠIN BUNAR",
            "Novi Beograd": "NOVI BEOGRAD",
            "Beograd Centar": "BEOGRAD CENTAR",
            "Karadjordjev Park": "KARAĐORĐEV PARK",
            "Vukov Spomenik": "VUKOV SPOMENIK",
            "Pancevacki Most": "PANČEVAČKI MOST",
            "Krnjaca Most": "KRNJAČA MOST",
            "Krnjaca": "KRNJAČA",
            "Sebes": "SEBEŠ",
            "Ovca": "OVČA",
            "Knezevac": "KNEŽEVAC",
            "Zemun Polje": "ZEMUN POLJE"
        }
        
        display_name = url_name_map.get(name, name.upper())
        # Properly encode spaces as %20 and special chars for the URL
        encoded_name = urllib.parse.quote(display_name)
        
        # We use 'polazak' (Departures) as per your second link
        url = f"https://w3.srbvoz.rs/redvoznje//stanicni/{encoded_name}/{s_id}/{today}/0000/polazak/999/sr"
        
        try:
            print(f"Scraping {name} via {url}...")
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # The Srbija Voz table usually sits inside a specific div or table
            rows = soup.find_all('tr')
            found_count = 0

            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                
                raw_type = cols[0].get_text(strip=True).upper()
                raw_id = cols[1].get_text(strip=True)
                
                # Check for BG:VOZ or train numbers starting with 80
                if any(x in raw_type for x in ["BG", "БГ"]) or raw_id.startswith('80'):
                    dep_time = cols[2].get_text(strip=True)
                    direction = normalize_text(cols[3].get_text(strip=True).upper())
                    note = cols[4].get_text(strip=True) if len(cols) > 4 else ""

                    line = "BG:voz 2" if any(k in direction for k in ["RESNIK", "MLADENOVAC", "LAZAREVAC"]) else "BG:voz 1"

                    if raw_id not in master_trains:
                        master_trains[raw_id] = {
                            "train_id": raw_id,
                            "line": line,
                            "direction": direction,
                            "note": note,
                            "stops": []
                        }
                    
                    # Ensure we don't add duplicate stops for the same station/train
                    if not any(s['station'] == name for s in master_trains[raw_id]["stops"]):
                        master_trains[raw_id]["stops"].append({"station": name, "departure": dep_time})
                        found_count += 1
            
            print(f"Found {found_count} BG:VOZ departures for {name}")

        except Exception as e:
            print(f"Error scraping {name}: {e}")

    # Convert to list and sort
    output = list(master_trains.values())
    for train in output:
        train["stops"].sort(key=lambda x: x["departure"])

    with open('trains.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved {len(output)} trains to trains.json")

if __name__ == "__main__":
    scrape()
