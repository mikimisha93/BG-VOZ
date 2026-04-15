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

# Use current date
today = datetime.now().strftime("%d.%m.%Y")
master_trains = {}

def scrape():
    # Headers make the script look like a real browser to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for name, s_id in STATIONS.items():
        # Srbija Voz URLs work better with uppercase names
        url = f"https://w3.srbvoz.rs/redvoznje//stanicni/{name.upper()}/{s_id}/{today}/0000/polazak/999/sr"
        
        try:
            print(f"Scraping {name}...")
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all table rows
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                
                # Check if it's a valid data row (must have at least 4 columns)
                if len(cols) < 4:
                    continue
                
                # Filter ONLY for BG:VOZ (checking both Latin and Cyrillic)
                train_type = cols[0].text.strip().upper()
                if "BG:VOZ" in train_type or "БГ:ВОЗ" in train_type:
                    
                    train_id = cols[1].text.strip()
                    dep_time = cols[2].text.strip()
                    direction = cols[3].text.strip().upper()
                    
                    # Grab 'Napomena' (Note) if available in the 5th column
                    note = cols[4].text.strip() if len(cols) > 4 else ""

                    # Determine Line 1 or Line 2 based on direction keywords
                    if any(key in direction for key in ["RESNIK", "REZNIK", "MLADENOVAC", "LAZAREVAC"]):
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
                    
                    # Add this station stop to the train's journey
                    master_trains[train_id]["stops"].append({
                        "station": name,
                        "departure": dep_time
                    })
                    
        except Exception as e:
            print(f"Error scraping {name}: {e}")

    # Convert dictionary to list and sort stops by departure time
    output = []
    for t_id in master_trains:
        master_trains[t_id]["stops"].sort(key=lambda x: x["departure"])
        output.append(master_trains[t_id])

    # Save to JSON file
    with open('trains.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved {len(output)} trains to trains.json")

if __name__ == "__main__":
    scrape()
