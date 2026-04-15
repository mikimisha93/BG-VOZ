import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Stations mapping with official IDs from Srbija Voz
STATIONS = {
    "Batajnica": "16204", "Kamendin": "16203", "Zemun Polje": "16053", 
    "Altina": "16059", "Zemun": "16052", "Tošin Bunar": "16202", 
    "Novi Beograd": "16051", "Beograd Centar": "16050", 
    "Karađorđev Park": "16208", "Vukov Spomenik": "16210", 
    "Pančevački Most": "16211", "Krnjača Most": "16214", 
    "Krnjača": "16213", "Sebeš": "16215", "Ovča": "16212",
    "Resnik": "16101", "Kijevo": "16207", "Kneževac": "16206", "Rakovica": "16001"
}

today = datetime.now().strftime("%d.%m.%Y")
master_trains = {}

def scrape():
    for name, s_id in STATIONS.items():
        url = f"https://w3.srbvoz.rs/redvoznje//stanicni/{name.upper()}/{s_id}/{today}/0000/polazak/999/sr"
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5 or "BG:VOZ" not in cols[0].text.upper() and "БГ:ВОЗ" not in cols[0].text.upper():
    continue
                
                train_id = cols[1].text.strip()
                dep_time = cols[2].text.strip()
                direction = cols[3].text.strip()
                
                # Check if there is a note (usually in the last column or hidden)
                # We'll grab the title attribute if it exists, or the text
                note = cols[4].text.strip() if len(cols) > 4 else ""

                if train_id not in master_trains:
                    master_trains[train_id] = {
                        "train_id": train_id,
                        "line": line,
                        "direction": direction,
                        "note": note, # Store the note here
                        "stops": []
                    }
                
                master_trains[train_id]["stops"].append({
                    "station": name,
                    "departure": dep_time
                })
        except Exception as e:
            print(f"Error scraping {name}: {e}")

    # Finalize and sort stops by time
    output = []
    for t_id, data in master_trains.items():
        data["stops"].sort(key=lambda x: x["departure"])
        output.append(data)

    with open('trains.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    scrape()
