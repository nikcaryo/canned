import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
gc = gspread.authorize(credentials)
spread = gc.open('canned test')

def test_sheets():
    print(spread.worksheets())

def delete(sheet,row,column):
    active = spread.worksheets()[sheet]
    for i in range(0,2):
        active.update_cell(row, column + i, '')
        print("deleted: " + str(sheet) + str(row) + str(column + i))
