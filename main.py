
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
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
        
        links = soup.find_all('a', href=lambda x: x and 'datail' in x)
        for link in links[:30]: # Limit for testing
            detail_url = urljoin("https://www.okasan-online.co.jp", link['href'])
            detail_soup = self.get_soup(detail_url)
            if not detail_soup: continue
            
            term_el = detail_soup.find('h2')
            if not term_el: continue
            term = term_el.get_text(strip=True)
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
            for link in links[:10]:
                detail_url = urljoin(url, link['href'])
                detail_soup = self.get_soup(detail_url)
                if not detail_soup: continue
                term_el = detail_soup.find('h1', class_='c-title-page')
                if not term_el: continue
                term = term_el.get_text(strip=True)
                reading = ""
                table = detail_soup.find('table', class_='c-table')
                if table:
                    reading_el = table.find('td')
                    if reading_el: reading = reading_el.get_text(strip=True)
                content = detail_soup.find('div', class_='pos-r') or detail_soup.find('div', id='contents')
                definition = " ".join([p.get_text(strip=True) for p in content.find_all('p') if len(p.get_text(strip=True)) > 15]) if content else ""
                if term and definition:
                    results.append({"term": term, "reading": reading, "definition": definition, "src": "Rakuten"})
        return results

class NomuraScraper(BaseScraper):
    def scrape_all(self):
        print("Scraping Nomura...")
        results = []
        url_chars = ['a', 'i', 'u', 'e', 'o', 'ka', 'ki', 'ku', 'ke', 'ko', 'sa', 'si', 'su', 'se', 'so', 'ta', 'ti', 'tu', 'te', 'to', 'na', 'ni', 'nu', 'ne', 'no', 'ha', 'hi', 'hu', 'he', 'ho', 'ma', 'mi', 'mu', 'me', 'mo', 'ya', 'yu', 'yo', 'ra', 'ri', 'ru', 're', 'ro', 'wa']
        for char in url_chars:
            url = f"https://www.nomura.co.jp/terms/{char}_index.html"
            soup = self.get_soup(url)
            if not soup: continue
            
            items = soup.find_all('li', class_='terms-list__item')
            for item in items:
                link = item.find('a')
                if link:
                    term = link.get_text(strip=True)
                    detail_url = urljoin(url, link['href'])
                    # We could scrape detail, but for Nomura, the list might have previews.
                    # Let's hit the detail page for quality.
                    detail_soup = self.get_soup(detail_url)
                    if detail_soup:
                        reading_el = detail_soup.find('p', class_='terms-detail__reading')
                        reading = reading_el.get_text(strip=True).strip('（）') if reading_el else ""
                        def_el = detail_soup.find('div', class_='terms-detail__body')
                        definition = def_el.get_text(strip=True) if def_el else ""
                        results.append({"term": term, "reading": reading, "definition": definition, "src": "Nomura"})
        return results

class DaiwaScraper(BaseScraper):
    def scrape_all(self):
        print("Scraping Daiwa...")
        results = []
        # Daiwa uses a complex navigation, but let's try the direct syllabary index if possible.
        # Actually, they have an index page: https://www.daiwa.jp/glossary/
        url = "https://www.daiwa.jp/glossary/"
        soup = self.get_soup(url)
        if not soup: return []
        
        links = soup.select('.glossary_list a')
        for link in links[:30]:
            detail_url = urljoin(url, link['href'])
            detail_soup = self.get_soup(detail_url)
            if not detail_soup: continue
            
            term_el = detail_soup.find('h1')
            if not term_el: continue
            term = term_el.get_text(strip=True)
            
            reading_el = detail_soup.find('p', class_='reading')
            reading = reading_el.get_text(strip=True) if reading_el else ""
            
            def_el = detail_soup.find('div', class_='explanation')
            definition = def_el.get_text(strip=True) if def_el else ""
            
            results.append({"term": term, "reading": reading, "definition": definition, "src": "Daiwa"})
        return results

class MUFGScraper(BaseScraper):
    def scrape_all(self):
        print("Scraping MUFG...")
        results = []
        url_chars = ['a', 'i', 'u', 'e', 'o', 'ka', 'ki', 'ku', 'ke', 'ko', 'sa', 'shi', 'su', 'se', 'so', 'ta', 'chi', 'tsu', 'te', 'to', 'na', 'ni', 'nu', 'ne', 'no', 'ha', 'hi', 'fu', 'he', 'ho', 'ma', 'mi', 'mu', 'me', 'mo', 'ya', 'yu', 'yo', 'ra', 'ri', 'ru', 're', 'ro', 'wa']
        for char in url_chars:
            url = f"https://www.sc.mufg.jp/learn/terms/{char}.html"
            soup = self.get_soup(url)
            if not soup: continue
            
            items = soup.select('.terms_list dt')
            for dt in items:
                term = dt.get_text(strip=True)
                dd = dt.find_next_sibling('dd')
                definition = dd.get_text(strip=True) if dd else ""
                results.append({"term": term, "reading": "", "definition": definition, "src": "MUFG"})
        return results

# --- Utility Functions ---

def rephrase_definition(definition):
    if not definition: return ""
    new_def = definition.replace("。です。", "。").replace("のことです。", "を意味します。")
    new_def = re.sub(r'といいます$', 'と呼ばれます。', new_def)
    new_def = re.sub(r'である$', 'を指します。', new_def)
    if len(new_def) > 300:
        new_def = new_def[:300] + "..."
    return new_def

def update_spreadsheet(all_data):
    import base64
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = '/Users/matsuyamakoichi/service-account.json' if os.path.exists('/Users/matsuyamakoichi/service-account.json') else 'service-account.json'
    
    if not os.path.exists(creds_path):
        creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        if creds_json:
            try:
                # Try base64 decoding first
                decoded = base64.b64decode(creds_json).decode('utf-8')
                with open('service-account.json', 'w') as f:
                    f.write(decoded)
                creds_path = 'service-account.json'
            except Exception:
                # If not base64, assume it's raw JSON
                with open('service-account.json', 'w') as f:
                    f.write(creds_json)
                creds_path = 'service-account.json'
        else:
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
        RakutenScraper(),
        NomuraScraper(),
        DaiwaScraper(),
        MUFGScraper()
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
