
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import time
import re
from urllib.parse import urljoin

# --- Scraper Classes ---

class BaseScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_soup(self, url, encoding='utf-8'):
        try:
            time.sleep(1) # Be polite
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = encoding
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

class SMBCNikkoScraper(BaseScraper):
    def scrape_all(self):
        print("Scraping SMBC Nikko...")
        results = []
        # chars in Japanese syllabary (a, i, u, e, o, ka, ki, ...)
        # Based on their URL structure
        url_chars = ['a', 'i', 'u', 'e', 'o', 'ka', 'ki', 'ku', 'ke', 'ko', 'sa', 'si', 'su', 'se', 'so', 'ta', 'ti', 'tu', 'te', 'to', 'na', 'ni', 'nu', 'ne', 'no', 'ha', 'hi', 'hu', 'he', 'ho', 'ma', 'mi', 'mu', 'me', 'mo', 'ya', 'yu', 'yo', 'ra', 'ri', 'ru', 're', 'ro', 'wa']
        for char in url_chars:
            url = f"https://www.smbcnikko.co.jp/terms/japan/{char}/index.html"
            soup = self.get_soup(url, encoding='shift_jis')
            if not soup: continue
            
            items = soup.find_all('li')
            for item in items:
                link_el = item.find('a', class_='link-list__type')
                if link_el:
                    full_text = link_el.get_text(strip=True)
                    match = re.search(r'(.+?)（(.+?)）', full_text)
                    term = match.group(1).strip() if match else full_text
                    reading = match.group(2).strip() if match else ""
                    definition = item.get_text(strip=True).replace(full_text, "").strip()
                    definition = re.sub(r'^[〉＞\s]+', '', definition)
                    if definition:
                        results.append({"term": term, "reading": reading, "definition": definition, "src": "SMBC"})
        return results

class OkasanScraper(BaseScraper):
    def scrape_all(self):
        print("Scraping Okasan Online...")
        results = []
        base_url = "https://www.okasan-online.co.jp/support/beginner/glossary/"
        index_url = base_url + "index.html"
        soup = self.get_soup(index_url)
        if not soup: return []
        
        # Find all detail links
        links = soup.find_all('a', href=lambda x: x and 'datail' in x)
        for link in links[:50]: # Limit for demo, can be removed for full run
            detail_url = urljoin("https://www.okasan-online.co.jp", link['href'])
            detail_soup = self.get_soup(detail_url)
            if not detail_soup: continue
            
            term_el = detail_soup.find('h2')
            if not term_el: continue
            term = term_el.get_text(strip=True)
            
            # Definition is the paragraphs after h2
            paragraphs = detail_soup.select('#main_content p')
            definition = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            
            results.append({"term": term, "reading": "", "definition": definition, "src": "Okasan"})
        return results

class RakutenScraper(BaseScraper):
    def scrape_all(self):
        print("Scraping Rakuten...")
        results = []
        url_chars = ['a', 'ka', 'sa', 'ta', 'na', 'ha', 'ma', 'ya', 'ra', 'wa']
        for char in url_chars:
            url = f"https://www.rakuten-sec.co.jp/web/market/dictionary/j/{char}/"
            soup = self.get_soup(url)
            if not soup: continue
            
            links = soup.find_all('a', href=lambda x: x and '.html' in x and '/dictionary/j/' in x)
            for link in links[:20]:
                detail_url = urljoin(url, link['href'])
                detail_soup = self.get_soup(detail_url)
                if not detail_soup: continue
                
                term_el = detail_soup.find('h1', class_='c-title-page')
                if not term_el: continue
                term = term_el.get_text(strip=True)
                
                # Reading table
                reading = ""
                table = detail_soup.find('table', class_='c-table')
                if table:
                    reading_el = table.find('td')
                    if reading_el: reading = reading_el.get_text(strip=True)
                
                # Definition
                content = detail_soup.find('div', class_='pos-r') or detail_soup.find('div', id='contents')
                if content:
                    paragraphs = content.find_all('p')
                    definition = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                else:
                    definition = ""
                
                if term and definition:
                    results.append({"term": term, "reading": reading, "definition": definition, "src": "Rakuten"})
        return results

# --- Utility Functions ---

def rephrase_definition(definition):
    if not definition: return ""
    # Basic rearrangement to make it unique
    new_def = definition.replace("。です。", "。").replace("のことです。", "を意味します。")
    new_def = re.sub(r'といいます$', 'と呼ばれます。', new_def)
    new_def = re.sub(r'である$', 'を指します。', new_def)
    
    # Trim if too long
    if len(new_def) > 300:
        new_def = new_def[:300] + "..."
    return new_def

def update_spreadsheet(all_data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = '/Users/matsuyamakoichi/service-account.json' if os.path.exists('/Users/matsuyamakoichi/service-account.json') else 'service-account.json'
    
    if not os.path.exists(creds_path):
        print("Credentials not found. Skipping sheet update.")
        return

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key('1JwA5HPNvMmNwADjyCDdNaRg2XPu2hzO9SFAo72qjBnw')
    ws = sh.worksheet('シート1')
    
    current_rows = ws.get_all_values()
    existing_terms = {row[1] for row in current_rows if len(row) > 1}
    
    new_rows = []
    for item in all_data:
        if item['term'] not in existing_terms:
            reading = item['reading']
            initial = reading[0] if reading else ""
            rephrased = rephrase_definition(item['definition'])
            new_rows.append([initial, item['term'], reading, rephrased])
            existing_terms.add(item['term'])
    
    if new_rows:
        ws.append_rows(new_rows)
        print(f"Added {len(new_rows)} new terms to the sheet.")
    else:
        print("No new terms to add.")

def main():
    merged_data = []
    
    scrapers = [
        SMBCNikkoScraper(),
        OkasanScraper(),
        RakutenScraper()
    ]
    
    for scraper in scrapers:
        try:
            data = scraper.scrape_all()
            merged_data.extend(data)
        except Exception as e:
            print(f"Error in {scraper.__class__.__name__}: {e}")
            
    if merged_data:
        update_spreadsheet(merged_data)

if __name__ == "__main__":
    main()
