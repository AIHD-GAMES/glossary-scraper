
import requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_smbcnikko():
    base_url = "https://www.smbcnikko.co.jp/terms/japan/{char}/index.html"
    chars = ['a', 'i', 'u', 'e', 'o']
    results = []
    
    for char in chars:
        url = base_url.format(char=char)
        print(f"Scraping {url}...")
        response = requests.get(url)
        response.encoding = 'shift_jis'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Terms are in <ul class="link-list__type"><li>...</li></ul> or similar
        items = soup.find_all('li')
        for item in items:
            link_el = item.find('a', class_='link-list__type')
            if link_el:
                full_text = link_el.get_text(strip=True)
                # Format is usually "Term (Reading)"
                match = re.search(r'(.+?)（(.+?)）', full_text)
                if match:
                    term = match.group(1).strip()
                    reading = match.group(2).strip()
                else:
                    term = full_text
                    reading = ""
                
                # Definition is usually text node following the <a>
                # Or sometimes inside the <li>
                definition = item.get_text(strip=True).replace(full_text, "").strip()
                # Remove small arrows or "Check" markers if present
                definition = re.sub(r'^[〉＞\s]+', '', definition)
                
                results.append({
                    "term": term,
                    "reading": reading,
                    "definition": definition,
                    "source": "SMBC Nikko"
                })
        time.sleep(1)
    return results

if __name__ == "__main__":
    data = scrape_smbcnikko()
    with open("smbc_terms.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Total terms scraped: {len(data)}")
