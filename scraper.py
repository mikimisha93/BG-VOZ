import requests
from bs4 import BeautifulSoup
import json
import unicodedata
from datetime import datetime

# Stations mapping - Names must match the IDs in your stationMap
STATIONS = {
    "Batajnica": "16204", "Kamendin": "16203", "Zemun Polje": "16053", 
    "Altina": "16059", "Zemun": "16052", "Tosin Bunar": "16202", 
    "Novi Beograd": "16051", "Beograd Centar": "16050", 
    "Karadjordjev Park": "16208", "Vukov Spomenik": "16210", 
    "Pancevacki Most": "16211", "Krnjaca Most": "16214", 
    "Krnjaca": "16213", "Sebes": "16215", "Ovca": "16212",
    "Resnik": "16101", "Kijevo": "16207", "Knezevac": "16206", "Rakovica": "16001"
}

today = datetime.now().strftime("%d.%m.%Y")
master_trains = {}

def normalize_text(text):
    """ Converts text like 'Pančevački' to 'Pancevacki' to match HTML precisely """
    if not text: return ""
    # Standardize 'đ' to 'dj' as it's not a standard accent
    text = text.replace('đ', 'dj').replace('Đ', 'Dj')
    # Remove other accents (č, ć, š, ž)
    return "".join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def scrape():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for name, s_id in STATIONS.items():
        # The URL works best with the official names (with accents)
        # So we use a temporary variable for the URL but keep 'name' clean for the JSON
        url_name = name.replace("Tosin", "Tošin").replace("Karadjordjev", "Karađorđev").replace("Pancevacki", "Pančevački").replace("Krnjaca", "Krnjača").replace("Sebes", "Sebeš").replace("Ovca", "Ovča")
        
        url = f"https://w3.srbvoz.rs/redvoznje//stanicni/{url_name.upper()}/{s_id}/{today}/0000/polazak/999/sr"
        
        try:
            print(f"Scraping {name}...")
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                
                train_type = cols[0].text.strip().upper()
                # Check for Latin and Cyrillic BG:VOZ labels
                if any(x in train_type for x in ["BG:VOZ", "БГ:ВОЗ", "БГ"]):
                    
                    train_id = cols[1].text.strip()
                    dep_time = cols[2].text.strip()
                    # We normalize the direction to Latin as well
                    direction = normalize_text(cols[3].text.strip().upper())
                    note = cols[4].text.strip() if len(cols) > 4 else ""

                    # Line detection logic
                    if any(key in direction for key in ["RESNIK", "REZNIK", "MLADENOVAC", "LAZAREVAC", "РЕЗНИК", "РЕСНИК"]):
                        line = "BG:voz 2"
                    else:
                        line = "BG:voz 1"

                    if train_id not in master_trains:
                        master_trains[train_id] = {
                            "train_id": train_id,
                            "line": line,
                            "direction": direction,
                            "note": note,
                            "stops": []
                        }
                    
                    # Save 'name' (the clean Latin version) to the JSON
                    master_trains[train_id]["stops"].append({
                        "station": name,
                        "departure": dep_time
                    })
                    
        except Exception as e:
            print(f"Error scraping {name}: {e}")

    output = []
    for t_id in master_trains:
        master_trains[t_id]["stops"].sort(key=lambda x: x["departure"])
        output.append(master_trains[t_id])

    with open('trains.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved {len(output)} trains to trains.json")

if __name__ == "__main__":
    scrape()
