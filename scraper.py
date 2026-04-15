import requests
from bs4 import BeautifulSoup
import json
import unicodedata
from datetime import datetime

# We will scrape the main line routes to catch all trains passing through
ROUTES = [
    {"from": "16204", "to": "16212", "name": "Line 1: Batajnica-Ovca"},
    {"from": "16212", "to": "16204", "name": "Line 1: Ovca-Batajnica"},
    {"from": "16101", "to": "16212", "name": "Line 2: Resnik-Ovca"},
    {"from": "16212", "to": "16101", "name": "Line 2: Ovca-Resnik"}
]

today = datetime.now().strftime("%d.%m.%Y")
master_trains = {}

def normalize_text(text):
    if not text: return ""
    text = text.replace('đ', 'dj').replace('Đ', 'Dj')
    return "".join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def scrape():
    session = requests.Session()
    # Using an even more generic header set
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    })

    for route in ROUTES:
        print(f"Checking Route: {route['name']}...")
        # This is the SEARCH URL, which is usually less restricted than the MONITOR URL
        url = f"https://w3.srbvoz.rs/redvoznje//direktni/{route['from']}/{route['to']}/{today}/0000/sr"
        
        try:
            response = session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Search results use a different table structure
            # We look for the train ID and the details link
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5: continue
                
                # In search: Col 0 is Train Type/ID, Col 1 is Dep, Col 2 is Arr
                train_info = cols[0].get_text(strip=True)
                
                if "BG:VOZ" in train_info.upper() or "БГ:ВОЗ" in train_info.upper():
                    # Extract the 4-digit ID
                    train_id = "".join(filter(str.isdigit, train_info))
                    if not train_id: continue

                    dep_time = cols[1].get_text(strip=True)
                    arrival_time = cols[2].get_text(strip=True)
                    
                    if train_id not in master_trains:
                        master_trains[train_id] = {
                            "train_id": train_id,
                            "line": "BG:voz 2" if "Line 2" in route['name'] else "BG:voz 1",
                            "direction": "OVCA" if route['to'] == "16212" else ("BATAJNICA" if route['to'] == "16204" else "RESNIK"),
                            "stops": []
                        }
                    
                    # Note: Search results only give start and end. 
                    # This is a fallback to at least show the train exists.
                    print(f"  -> Found Train {train_id}")

        except Exception as e:
            print(f"  -> Error: {e}")

    # Save data
    output = list(master_trains.values())
    with open('trains.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"\nFinal count: {len(output)} trains found via Search Method.")

if __name__ == "__main__":
    scrape()
