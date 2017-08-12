import gspread
from oauth2client.service_account import ServiceAccountCredentials

CHARS = ['A', 'B', 'C', 'D', 'E','F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']


scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
gc = gspread.authorize(credentials)
spread = gc.open('canned test')
sheets = spread.worksheets()
