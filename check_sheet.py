
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def check_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/matsuyamakoichi/service-account.json', scope)
    client = gspread.authorize(creds)
    
    spreadsheet_id = '1JwA5HPNvMmNwADjyCDdNaRg2XPu2hzO9SFAo72qjBnw'
    sh = client.open_by_key(spreadsheet_id)
    print(f"Spreadsheet Title: {sh.title}")
    for i, worksheet in enumerate(sh.worksheets()):
        print(f"Sheet {i}: {worksheet.title}")

if __name__ == "__main__":
    check_sheet()
