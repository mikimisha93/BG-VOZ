import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Let's test just ONE station first to see if we can break the wall
STATIONS = {
    "Batajnica": "16204", "Beograd Centar": "16050", "Vukov Spomenik": "16210", "Ovca": "16212"
}

today = datetime.now().strftime("%d.%m.%Y")

def scrape():
    # iPhone User-Agent is often the "Golden Ticket" to bypass bot detection
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'sr-RS,sr;q=0.9',
        'Referer': 'https://www.srbvoz.rs/'
    }

    master_trains = {}

    for name, s_id in STATIONS.items():
        print(f"Attempting {name}...")
        # We'll use the simplest URL possible
        url = f"https://w3.srbvoz.rs/redvoznje//stanicni/BEOGRAD/{s_id}/{today}/0000/polazak/999/sr"
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            print(f"  HTTP Status: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Check if there is ANY table on the page
            table = soup.find('table')
            
            if not table:
                print("  -> No table found. Site might be blocking or page is empty.")
                continue

            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    train_id = cols[1].get_text(strip=True)
                    if train_id.isdigit():
                        if train_id not in master_trains:
                            master_trains[train_id] = {"id": train_id, "stops": []}
                        master_trains[train_id]["stops"].append(name)
            
            print(f"  -> Successfully read page for {name}")

        except Exception as e:
            print(f"  -> Error: {e}")

    print(f"\nFinal Test Count: {len(master_trains)} unique trains.")
    
    # Save empty list or data so the app doesn't crash
    with open('trains.json', 'w') as f:
        json.dump(list(master_trains.values()), f)

if __name__ == "__main__":
    scrape()
